
#include <omp.h>

#include "metisfl/controller/aggregation/secure_aggregation.h"
#include "metisfl/encryption/palisade/ckks_scheme.h"
#include "metisfl/proto/model.pb.h"

namespace metisfl::controller {

SecAgg::SecAgg(const EncryptionConfig &encryption_config) {
  encryption_config_ = encryption_config;
  if (encryption_config_.has_he_scheme()) {
      auto he_scheme_ = encryption_config.he_scheme();
      if (he_scheme_.has_ckks_scheme()) {
        encryption_scheme_.reset(new CKKS(
            he_scheme_.ckks_scheme().batch_size(),
            he_scheme_.ckks_scheme().scaling_factor_bits()));
        auto crypto_context = he_scheme_.he_scheme_config().crypto_context();
        encryption_scheme_->LoadCryptoContextFromFile(crypto_context);
      }
  } else {
      throw std::runtime_error("Unsupported encryption scheme.");
  }
}

FederatedModel
SecAgg::Aggregate(std::vector<std::vector<std::pair<const Model*, double>>>& pairs) {

  // Throughout this implementation, we use the first model provided in the pair.
  // If only one learner is given for the aggregation step, then we set its scaling
  // factor value to 1, else we use the precomputed scaling factors.
  // We create scaling factors / local models contribution values as floats because
  // the signature of the computeWeightedAverage() function in the FHE_Helper API
  // is expecting a vector of floats.
  std::vector<float> local_models_contrib_value;
  if (pairs.size() == 1) {
    local_models_contrib_value.emplace_back(1.0f);
  } else {
    for (const auto &pair : pairs) {
      const auto scale = (float) pair.front().second;
      local_models_contrib_value.emplace_back(scale);
    }
  }

  // Initializes the global model architecture using the definitions
  // of the first given model in the model pairs collection.
  FederatedModel global_model;
  const auto& sample_model = pairs.front().front().first;
  for (const auto &sample_variable: sample_model->variables()) {
    auto *variable = global_model.mutable_model()->add_variables();
    variable->set_name(sample_variable.name());
    variable->set_trainable(sample_variable.trainable());
    if (sample_variable.has_ciphertext_tensor()) {
      *variable->mutable_ciphertext_tensor()->mutable_tensor_spec() =
          sample_variable.ciphertext_tensor().tensor_spec();
      *variable->mutable_ciphertext_tensor()->mutable_tensor_spec()->mutable_value() = "";
    } else {
      throw std::runtime_error("Only Ciphertext variables are supported.");
    }
  }

  auto total_variables = global_model.model().variables_size();
  // Parallelize encrypted aggregation of model variables.
#pragma omp parallel for
  for (int var_idx = 0; var_idx < total_variables; ++var_idx) {
    std::vector<std::string> local_variable_ciphertexts;
    for (const auto &pair : pairs) {
      const auto *model = pair.front().first;
      local_variable_ciphertexts.emplace_back(
          model->variables(var_idx).ciphertext_tensor().tensor_spec().value());
    }
    // The `Aggregate` function assumes that each learner's contribution value,
    // scaling factor is already normalized / scaled.
    auto pwa_result =
        encryption_scheme_->Aggregate(local_variable_ciphertexts, local_models_contrib_value);        
    *global_model.mutable_model()->mutable_variables(var_idx)->
        mutable_ciphertext_tensor()->mutable_tensor_spec()->mutable_value() =
        pwa_result;
  }

  // Sets the number of contributors to the number of input models.
  global_model.set_num_contributors(pairs.size());
  return global_model;

}

void SecAgg::Reset() {
  // pass
}

} // namespace metisfl::controller
