# New evaluation families, fixed before H1 evaluation

Use the conventions in `../docs/formulation.md`, including symbolic d and generic
kinematics. Every target is non-scaleless, has nonnegative indices, and has total
propagator power at most rmax. This is the same target-generation rule as before.

| Family | Internal squared masses | Nonzero pair distances S_ij | rmax | Designated basis |
|---|---|---|---:|---|
| bubble_one_mass | (0,m) | S01=s | 5 | (0,1), (1,1) |
| triangle_two_mass | (0,0,0) | S02=s, S12=t | 4 | (1,0,1), (0,1,1) |
| box_one_mass | (0,0,0,0) | S02=s, S13=t, S03=u | 5 | (1,0,1,0), (0,1,0,1), (1,0,0,1), (1,1,1,1) |

The triangle/box names refer to off-shell external invariants, not massive internal
propagators. The bubble has one massive internal line. The massless box from the
initial suite is additionally evaluated as an exposed regression case; it is not
counted among the three new cases.

The original and independent checker definitions are explicit in `ibp/families.py`
and `ibp/validator.py`. The benchmark never specializes d or the invariants to
sample values. No extra master may be introduced to make a candidate appear complete.
