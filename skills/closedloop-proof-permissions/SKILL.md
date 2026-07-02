---
name: "closedloop-proof-permissions"
description: "Log and test proof permission requests for selected ClosedLoop AI proof candidates. Uses create_proof_permission_request, get_proof_permission_request, and update_proof_permission_status. Logs fake email only; never sends customer email."
---

# ClosedLoop AI Proof Permissions

Log a fake permission email for a selected proof candidate and update its test-only status.

This skill governs:

- `create_proof_permission_request`
- `get_proof_permission_request`
- `update_proof_permission_status`

Use this only after the user selects a candidate from `closedloop-sales-proof`, `closedloop-reference-customers`, `closedloop-case-study-scout`, or `closedloop-customer-proof`.

## Create A Request

Prefer the selected candidate's returned `follow_up_actions[0].params`.

Call:

```text
create_proof_permission_request(
  ...follow_up_actions[0].params,
  sender_name="{sender name if provided}",
  user_role="{sender role if provided}"
)
```

The tool logs a fake email body and returns a request id. It does not send anything to the customer.

## Read A Request

Call:

```text
get_proof_permission_request(request_id="{request_id}")
```

## Approve Or Deny For Testing

Call:

```text
update_proof_permission_status(
  request_id="{request_id}",
  status="approved" | "denied" | "pending",
  note="{optional test note}",
  actor_name="{optional actor}"
)
```

## Present Results

Use this structure:

```text
PROOF PERMISSION REQUEST
========================

Test status: {request.test_status}
Sent: no
Scope: {request.usage_scope}
Customer: {request.person.name or email}
Account: {request.account.name}

FAKE EMAIL LOG
To: {request.fake_email.to}
Subject: {request.fake_email.subject}

{request.fake_email.body}

TEST ACTIONS
- Approve: update_proof_permission_status(...status="approved")
- Deny: update_proof_permission_status(...status="denied")
```

## Feedback To ClosedLoop AI

If the permission request, fake email, evidence, or test-status flow looks wrong, missing, stale, or confusing, explicitly invite the user to send feedback about ClosedLoop AI. If they ask you to send it, use `closedloop-send-feedback` or call `send_closedloop_feedback(content=...)`. Strip PII and customer-specific details.

## Rules

- Never send customer email.
- Never claim approval until `test_status` is `approved`.
- A logged fake email is not proof of consent.
- Keep permission scope explicit: `website`, `sales`, `case_study`, or `live_reference`.
- Use returned request ids; do not invent ids.
