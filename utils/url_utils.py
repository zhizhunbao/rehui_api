from urllib.parse import urlparse


def extract_listing_id(url: str) -> str:
    # ======== 参数变量 ========
    anchor_key   = "listing="            # listing 段开头
    separator    = "/"                   # 分隔符
    index_target = 0                     # listing_id 是第一个段

    # ======== 中间变量 ========
    fragment     = urlparse(url).fragment
    anchor_value = fragment.split(anchor_key)[-1]
    listing_id   = anchor_value.split(separator)[index_target]

    return listing_id