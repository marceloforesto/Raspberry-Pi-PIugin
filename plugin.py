import os
from os.path import basename
import datetime
import zipfile
import time
import RPi.GPIO as GPIO
from glob import glob
from subprocess import check_output, CalledProcessError

def get_usb_devices():  #funcao auxiliar da funcao get_mount_points()

  sdb_devices = map(os.path.realpath, glob('/sys/block/sd*'))

  usb_devices = (dev for dev in sdb_devices

      if 'usb' in dev.split('/')[5])

  return dict((os.path.basename(dev), dev) for dev in usb_devices)

def get_mount_points(devices=None): #funcao que retorna o diretorio do pendrive montado pelo SO

  devices = devices or get_usb_devices() # if devices are None: get_usb_devices

  output = check_output(['mount']).splitlines()

  is_usb = lambda path: any(dev in path for dev in devices)

  usb_info = (line for line in output if is_usb(line.split()[0]))

  pathString =  str([info.split()[2] for info in usb_info])

  pathString = pathString.replace('[', '')

  pathString = pathString.replace(']', '')

  return pathString

def zip(src, dst):  #funcao que compacta um diretorio

  zf = zipfile.ZipFile("%s.zip" % (dst), "w", zipfile.ZIP_DEFLATED)

  abs_src = os.path.abspath(src)

  for dirname, subdirs, files in os.walk(src):

    for filename in files:

      absname = os.path.abspath(os.path.join(dirname, filename))
          
      arcname = absname[len(abs_src) + 1:]

      print 'zipping %s as %s' % (os.path.join(dirname, filename), arcname)

      zf.write(absname, arcname)

  zf.close()

def zip_and_move_file():  #zip o diretorio ftp_dir e move para o pendrive inserido

  now = datetime.datetime.now()

  filename =  now.strftime("%Y-%m-%d_%H-%M-%S")   #string que usada para nomear o arquivo .zip que possui a hora e a data em que o botao foi prescionado

  zip('/home/pi/Documents/ftp_dir', filename)   #realiza a criacao do arquivo .zip

  os.system("sudo mv "+filename+".zip "+get_mount_points()+" && umount "+get_mount_points())    #move o arquivo .zip e desmonta o pendrive



if __name__ == '__main__':

  try:

    GPIO.setmode(GPIO.BOARD)  #seta os IO do botao e do led

    ledPin = 12   #IO do led
      
    buttonPin = 7   #IO do botao

    GPIO.setup(ledPin, GPIO.OUT)
      
    GPIO.setup(buttonPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)


    while True:

        buttonState = GPIO.input(buttonPin)   #recebe  

        if buttonState == False and get_mount_points() != '': #verifica se o botao foi precionado e se ha um pendrive na raspberry pi

          zip_and_move_file()   #chama a funcao que realiza as operacoes
            
          GPIO.output(ledPin, GPIO.HIGH)  #acende o led

          time.sleep(5) #timer de 5 segundos para o led continuar acesso

        else:

          GPIO.output(ledPin, GPIO.LOW)   #caso desliga o led

  except (KeyboardInterrupt):

    GPIO.cleanup()