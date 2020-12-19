export function isRejectedAction(action) {
  return action.type.endsWith("rejected");
}
