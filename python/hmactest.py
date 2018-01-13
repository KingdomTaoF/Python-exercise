import hmac
h = hmac.new(b'天王盖地虎', b'宝塔镇河妖')
print h.hexdigest() 