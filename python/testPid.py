YTimport os
import sys
import subprocess

def isActive(pid):
  try:
    os.kill(pid,0)
    return True
  except:
    return False

def getPid():
  args = ['ps', 'ax']
  args2 = ['grep', 'serial_only_ttag.py']
  #args = ['ls', '-l']
  #f = open("pid.txt", 'w')
  p = subprocess.Popen(args, stdout = subprocess.PIPE)
  output = subprocess.check_output(args2, stdin = p.stdout)
  p.wait()
  #f.close()
  return output
  
if __name__ == "__main__":
  #pid = int(sys.argv[1])
  #print isActive(pid)
  output = getPid()
  print output 
  outList = [int(s) for s in output.split() if s.isdigit()]
  print outList

