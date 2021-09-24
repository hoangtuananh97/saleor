class ProductClassRecommendationType:
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    APPROVED = "APPROVED"

    CHOICES = [
        (DRAFT, "Initial product class recommendation"),
        (SUBMITTED, "Product class submitted, waiting for approval"),
        (APPROVED, "Product class approved"),
    ]
