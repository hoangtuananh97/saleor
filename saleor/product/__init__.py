default_app_config = "saleor.product.app.ProductAppConfig"


class ProductMediaTypes:
    IMAGE = "IMAGE"
    VIDEO = "VIDEO"

    CHOICES = [
        (IMAGE, "An uploaded image or an URL to an image"),
        (VIDEO, "A URL to an external video"),
    ]


class ProductClassRecommendationType:
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    APPROVED = "APPROVED"

    CHOICES = [
        (DRAFT, "Initial product class recommendation"),
        (SUBMITTED, "Product class submitted, waiting for approval"),
        (APPROVED, "Product class approved"),
    ]
