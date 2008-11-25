# -*- coding: utf-8 -*-
import Pointything

if __name__ == "__main__":
    pthang = Pointything.Pointything()
    pthang.extendWith(Pointything.ExtensionControl())
    print pthang.do("concat","Result of loading StringTransform: ",pthang.do("loadModule","StringTransform"))
    print pthang.do("concat","Extensions: ",pthang.do("listExtensions"))
    print pthang.do("concat","Functions: ", pthang.do("listFunctions"))
    print pthang.do("concat", "Hello"," ").do("concat", "World!"," ").do("concat","how"," ").do("concat","are", " ").do("concat","you")
    print pthang.do("concat", "Reversed 'hello':"," ",pthang.do("reverse", "hello"))
    out = pthang.do("concat", "Ho", "dy")
    out = pthang.do("reverse", out)
    print pthang.do("concat", "Reversed howdy bits:", " ", out)