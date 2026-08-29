import type { PendingCall } from "../types";

interface Props {
  pendingCall: PendingCall;
  busy: boolean;
  onDecision: (approve: boolean) => void;
}

export default function ConfirmBar({ pendingCall, busy, onDecision }: Props) {
  return (
    <div className="confirm-bar">
      <div>
        <b>⚠ Confirmation needed</b>
        <p>
          The agent wants to run <code>{pendingCall.name}</code> with:
        </p>
        <pre>{JSON.stringify(pendingCall.args, null, 2)}</pre>
      </div>
      <div className="confirm-actions">
        <button disabled={busy} onClick={() => onDecision(true)}>
          Approve
        </button>
        <button disabled={busy} className="ghost" onClick={() => onDecision(false)}>
          Reject
        </button>
      </div>
    </div>
  );
}
