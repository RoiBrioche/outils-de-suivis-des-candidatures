# 03-validation-errors.md

## Validation Layer
- Django Forms or ModelForms
- Model-level constraints where possible
- Clean methods for business rules

## Validation Categories

### Field Validation
- Required fields enforced
- Type validation (dates, strings)
- Max length constraints

### Business Validation
- Application date must belong to its period
- Only one active period allowed
- Status transitions constrained

## Error Handling
- ValidationError for user-correctable issues
- IntegrityError guarded at ORM level
- 400 responses for validation failures
- 500 responses for unexpected errors

## Error Format
- Field-level error mapping
- Non-field errors explicitly identified
