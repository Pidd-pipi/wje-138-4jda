class BusinessValidationError(Exception):
    """业务规则校验失败（如保养到期车辆被调度），由视图层转 400。"""

    def __init__(self, detail):
        self.detail = detail
        super().__init__(detail)
