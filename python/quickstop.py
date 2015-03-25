import ttag
buf = ttag.TTBuffer(0)
buf.stop()
for i in range(10):
	ttag.deletebuffer(i)

