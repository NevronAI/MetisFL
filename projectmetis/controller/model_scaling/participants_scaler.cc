
#include "projectmetis/controller/model_scaling/participants_scaler.h"

namespace projectmetis::controller {

absl::flat_hash_map<std::string, double>
ParticipantsScaler::ComputeScalingFactors(
    const FederatedModel &community_model,
    const absl::flat_hash_map<std::string, LearnerState*> &states,
    const absl::flat_hash_map<std::string, TaskExecutionMetadata*> &metadata) {

  /*
   * For a single learner the scaling factor is the identity value (=1).
   * For multiple learners, the scaling factors are the weighted average of all identities (=1/N).
   */
  auto num_participants = states.size();
  absl::flat_hash_map<std::string, double> scaling_factors;
  if (num_participants == 1) {

    auto learner_id = states.begin()->first;
    scaling_factors[learner_id] = 1;

  } else {

    for (const auto &[learner_id, state]: states) {
      double scaling_factor =
          static_cast<double>(1) / static_cast<double>(num_participants);
      scaling_factors[learner_id] = scaling_factor;
    }

  }

  return scaling_factors;

}

} // namespace projectmetis::controller
