from src.tools import router
def test_valid(): assert router.execute("calculator",{"expression":"2*(3+4)"})["result"]==14
def test_extra_field_rejected():
 try: router.validate("calculator",{"expression":"2+2","x":1}); assert False
 except Exception: pass
def test_unsafe(): assert "error" in router.execute("calculator",{"expression":"__import__('os').system('echo hi')"})
def test_names_rejected(): assert "error" in router.execute("calculator",{"expression":"os.getcwd()"})
