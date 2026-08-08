                    ┌──────────────────────┐
                    │      REGISTER        │
                    └──────────┬───────────┘
                               │
                               ▼
                    Create User
                    is_verified = false
                               │
                               ▼
                 Send Verification Email
                               │
                               ▼
                  /verify-email?token=...
                               │
                     Token present?
                      │          │
                     YES         NO
                      │          │
                      ▼          ▼
               Verify automatically
                               │
                               ▼
                    Email verified
                               │
                               ▼
                 Issue Access + Refresh
                               │
                               ▼
                       GET /manifest
                               │
                               ▼
                 ┌────────────────────────┐
                 │   Application State    │
                 │                        │
                 │ User                   │
                 │ Organizations          │
                 │ Invitations            │
                 │ Onboarding             │
                 └───────────┬────────────┘
                             │
                             ▼
                   Onboarding complete?
                       │           │
                      YES          NO
                       │           │
                       ▼           ▼
                   Dashboard   Pending invitation?
                                  │          │
                                 YES         NO
                                  │          │
                                  ▼          ▼
                         Accept invitation  Has organization?
                                  │          │
                                  ▼         YES / NO
                         Organization        │
                           Member            │
                                  │          ├── YES → Dashboard
                                  │          │
                                  │          └── NO
                                  │               │
                                  │               ▼
                                  │        Create Organization
                                  │               │
                                  └───────────────┘
                                          │
                                          ▼
                                      Dashboard
