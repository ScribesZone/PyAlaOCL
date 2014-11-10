import time
from pymodelio.core.env import PyModelioEnv
from expectj import ExpectJ
import os

OUT = ""
ERR = ""
def readOutput(process):
    global OUT
    out_size = len(OUT)
    new_out = process.getCurrentStandardOutContents()
    if len(new_out) == out_size:
        return ""
    else:
        OUT = new_out
        return OUT[out_size:]
        

#  print '==OUT OUT OUT==========================='
#  print s.getCurrentStandardOutContents() + "@"
#  print '>>>ERR ERR ERR >>>>>>>>>>>>>>>>>>>>>>>>>>>>'
#  print s.getCurrentStandardErrContents() + "@@"
#  print '*****************************************************************'
#  print
e = ExpectJ(2)
s = e.spawn('cmd /c c:\\S\\use3.0.6\\bin\\use.bat -nogui')
s.expect('use> ')
print 'LAUNCH '+'*'*50
print readOutput(s)
print '**\n'*5

if True:
    print 'help '+'*'*50
    s.send('help\r\n')
    time.sleep(5)
    s.expect('use> ')
    print readOutput(s)
    print '**\n'*5

print '? Set{1,2}->size() '+'*'*50
s.send('? Set{1,2}->size()\r\n')
time.sleep(1)
s.expect('use>')
print readOutput(s)
print '**\n'*5

print '? Set{}->size() '+'*'*50
s.send('? Set{}->size()\r\n')
time.sleep(1)
s.expect('use> ')
print readOutput(s)
print '**\n'*5

s.send('quit\r\n')
s.expectClose()
print '----------------------'
print OUT
print "EXIT CODE=%s" % s.getExitValue()
if not s.isClosed():
  print "kill the process"
  s.stop()