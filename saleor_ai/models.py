from django.db import models

from saleor import settings


class SaleorAI(models.Model):
    scgh_mch3_code = models.CharField(max_length=5, null=True, blank=True)
    scgh_mch3_desc = models.CharField(max_length=256, null=True, blank=True)
    scgh_mch2_code = models.CharField(max_length=5, null=True, blank=True)
    scgh_mch2_desc = models.CharField(max_length=256, null=True, blank=True)
    scgh_mch1_code = models.CharField(max_length=5, null=True, blank=True)
    scgh_mch1_desc = models.CharField(max_length=256, null=True, blank=True)
    brand = models.CharField(max_length=50, null=True, blank=True)
    article_code = models.CharField(max_length=50, null=True, blank=True)
    article_name = models.CharField(max_length=256, null=True, blank=True)
    item_flag = models.CharField(max_length=50, null=True, blank=True)
    item_status = models.CharField(max_length=50, null=True, blank=True)
    scgh_dc_item_flag = models.CharField(max_length=10, null=True, blank=True)
    scgh_dc_stock = models.CharField(max_length=50, null=True, blank=True)
    scgh_show_no_stock_flag = models.CharField(max_length=10, null=True, blank=True)
    scgh_product_class = models.CharField(max_length=250, null=True, blank=True)
    scgh_vmi_flag = models.CharField(max_length=10, null=True, blank=True)
    scgh_showroom_flag = models.CharField(max_length=10, null=True, blank=True)
    scgh_market_flag = models.CharField(max_length=10, null=True, blank=True)
    scgh_shop_flag = models.CharField(max_length=10, null=True, blank=True)
    sales_uom = models.CharField(max_length=10, null=True, blank=True)
    sales_price = models.IntegerField(default=0, null=True, blank=True)
    purchase_uom = models.CharField(max_length=10, null=True, blank=True)
    purchase_price = models.DecimalField(
        max_digits=settings.DEFAULT_MAX_DIGITS,
        decimal_places=settings.DEFAULT_DECIMAL_PLACES,
        default=0,
    )
    purchase_group = models.CharField(max_length=10, null=True, blank=True)
    moq = models.CharField(max_length=10, null=True, blank=True)
    vendor_code = models.CharField(max_length=50, null=True, blank=True)
    vendor_name = models.CharField(max_length=256, null=True, blank=True)
    comp_code = models.CharField(max_length=50, null=True, blank=True)
    comp_desc = models.CharField(max_length=256, null=True, blank=True)
    dc_rdc_code = models.CharField(max_length=50, null=True, blank=True)
    dc_rdc_desc = models.CharField(max_length=256, null=True, blank=True)
    franchise_code = models.CharField(max_length=50, null=True, blank=True)
    franchise_desc = models.CharField(max_length=256, null=True, blank=True)
    actual_sales_value = models.IntegerField(default=0)
    actual_sales_qty = models.IntegerField(default=0)
    forecast_value = models.DecimalField(
        max_digits=settings.DEFAULT_MAX_DIGITS,
        decimal_places=settings.DEFAULT_DECIMAL_PLACES,
        default=0,
    )
    forecast_qty = models.IntegerField(default=0)
    safety_stock_qty = models.IntegerField(default=0)
    min_qty = models.IntegerField(default=0)
    max_qty = models.IntegerField(default=0)
    product_class_qty = models.CharField(max_length=50, null=True, blank=True)
    product_class_value = models.CharField(max_length=50, null=True, blank=True)
    product_class_default = models.CharField(max_length=50, null=True, blank=True)
    start_of_week = models.DateField(null=True, blank=True)
    start_of_month = models.DateField(null=True, blank=True)

    class Meta:
        app_label = "saleor_ai"
