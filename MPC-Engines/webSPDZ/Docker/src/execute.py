
import sys, re, os, time
import shutil
import tempfile
# import subprocess

# selenium stuff (:
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
# from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from webdriver_manager.firefox import GeckoDriverManager as DriverManager

# os.system('ls -l /home/.cache')

# ==================================================================================================
def get_temp_browser_exec_path(path, verbose=False):
  tmp_path = tempfile.NamedTemporaryFile(delete=False).name
  shutil.copy(path, tmp_path)
  os.chmod(tmp_path, 0o755)

  if (verbose==True):
    print('given path: ', path)
    print('temporary path: ', tmp_path)

  return tmp_path

# ==================================================================================================
def init_driver():
  # 🎛 Set up options, service, ...
  options = FirefoxOptions()

  # 🐳 in Docker (w/o GUI)
  options.add_argument('--headless')
  # 🌐🔄 WebRTC (PeerJS) stuff
  options.set_preference('javascript.options.shared_memory', True)
  options.set_preference('javascript.options.self_hosted.use_shared_memory', True)
  options.set_preference("privacy.file_unique_origin", False)
  options.set_preference("media.navigator.permission.disabled", True) # auto-grant mic/cam
  options.set_preference("media.navigator.streams.fake", True) # use fake streams
  options.set_preference("media.peerconnection.enabled", True) # ensure WebRTC is on
  # 🧪 Ignore self-signed certificate errors
  options.set_capability("acceptInsecureCerts", True)
  options.set_preference("security.cert_pinning.enforcement_level", 0)  # Allow self-signed
  options.set_preference("webdriver_accept_untrusted_certs", True)
  options.set_preference("webdriver_assume_untrusted_issuer", True)

  # required from HTTPS server to be able to use SharedArray buffer:
  # ..Cross-Origin-Opener-Policy: same-origin
  # ..Cross-Origin-Embedder-Policy: require-corp

  profile=webdriver.FirefoxProfile()
  profile.set_preference("network.websocket.allowInsecureFromHTTPS", True)
  profile.set_preference("dom.postMessage.sharedArrayBuffer.bypassCOOP_COEP.insecure.enabled", True)
  # profile.set_preference("dom.postMessage.sharedArrayBuffer.bypassCOOP_COEP.insecure.enabled", False)
  profile.set_preference("dom.postMessage.sharedArrayBuffer.withCOOP_COEP", True)
  profile.set_preference("dom.origin-trials.coep-credentialless.state", 1)
  profile.update_preferences()

  if (profile != None):
    options.profile=profile

  # options.binary_location='/bin/firefox' # <-- handled by GeckoDriverManager()
  # print('before DriverManager.install')
  # print('after DriverManager.install')
  # time.sleep(2)

  geckodriver_version = 'v0.36.0'
  geckodriver_info_url = 'https://github.com/mozilla/geckodriver/releases'
  try:
    ## trying to fix the path to avoid 'text file busy' complaints
    print(f'...BE AWARE: Geckodriver version fixed to "{geckodriver_version}" to avoid too many API requests ^^ (-> {geckodriver_info_url})')
    browser_binary_path_original = f'/home/.wdm/drivers/geckodriver/linux64/{geckodriver_version}/geckodriver'
    browser_binary_path = get_temp_browser_exec_path(browser_binary_path_original)
    print('...using temp. Gecko binary bath')
  except Exception as e:
    print('...no temp. Gecko binary path, using DriverManager: ', e)
    browser_binary_path = DriverManager(version=geckodriver_version).install()

  # options.binary_location = '/bin/firefox-nightly'
  # options.executable_path = '/home/.cache/selenium/geckodriver/linux64/0.35.0/geckodriver'
  # service =FirefoxService(log_output=subprocess.STDOUT)
  service = FirefoxService(browser_binary_path)
  driver = webdriver.Firefox(options=options, service=service)

  browser_name    = driver.capabilities['browserName']
  browser_version = driver.capabilities['browserVersion']
  print(f'Browser Name: {browser_name} ... Version: {browser_version}')

  # print('DRIVER first: ', DRIVER)
  # DRIVER=driver
  # print('DRIVER after: ', DRIVER)
  return driver


# ==================================================================================================
def print_HTML_body(driver):
  print('='*80, "\nWhole website's HTML Body:\n", get_HTML_body(driver))


# ==================================================================================================
def get_HTML_body(driver):
  return driver.find_element(By.XPATH, "/html/body").text


# ==================================================================================================
def print_console(driver):
  log_list = get_terminal_log(driver)
  log = log_list
  # log = ''.join(log_list)
  # log = strip_ansi(''.join(log_list))
  print('\n', '-'*30, '\nCONSOLE: \n', log)
  error_logs = driver.execute_script("return window.loggedErrors;")
  print(f'\nERROR LOG:\n{error_logs}')


# ==================================================================================================
# actually, (currently) returns a log list ^^
def get_terminal_log(driver, verbose=False):
    logs = driver.execute_script("return window.loggedMessages;")

    if (verbose==True): 
      print('='*80, '\nBrowser LOG:\n')
      for log in logs:
        print(log) 
    # print('\n', logs)

    # in case 'window.loggedMessages' doesn't work for Chrome:
    # if (BROWSE_CHROME==True):
    #   # Print browser console logs
    #   for entry in party_driver.get_log("browser"):
    #       print(entry)

    return logs


# ==================================================================================================
def store_console_logs(driver):
  # Inject JS to override console.log and store logs
  log_hook = '''
      window.loggedMessages = [];
      const originalLog = console.log;
      console.log = function(...args) {
          window.loggedMessages.push(args.join(" "));
          originalLog.apply(console, args);
      };

      window.loggedErrors = [];
      const originalError = console.error;
      console.error = function(...args) {
          window.loggedErrors.push(args.join(" "));
          originalError.apply(console, args);
      };
  '''
  driver.execute_script(log_hook)
  # driver.execute_script("localStorage.debug = 'peerjs,*';")
  driver.execute_script("console.log('this is a test LOG :D');")


# ==================================================================================================
def exit_race(driver, ex=True):
  driver.quit()
  if (ex==True):
    sys.exit(0)


# ==================================================================================================
def main():
  URL=sys.argv[1]

  party_driver = init_driver()
  store_console_logs(party_driver)

  # print_HTML_body(party_driver)
  # print_console(party_driver)
  # exit_race(party_driver, True)

  party_driver.set_page_load_timeout(60) # in seconds
  print("getting url: ", URL)
  try:
    party_driver.get(URL)
  except Exception as e:
    print_HTML_body(party_driver)
    print_console(party_driver)
    print("page load timeout reached: ", e)
    exit_race(party_driver, True)

  print("after getting url...now in while-waiting loop..")
  # print_HTML_body(party_driver)
  # print_console(party_driver)
  # exit_race(party_driver, True)

  cnt=0
  while True:
    time.sleep(5)
    # print("Whole website's HTML Body:\n", driver.find_element(By.XPATH, "/html/body").text)
    try:
      value = str(party_driver.find_element(By.ID, "output").get_attribute("value"))
    except Exception as e:
      print_HTML_body(party_driver)
      print_console(party_driver)
      print("\n..exception while looking for 'output' ID: ", e)
      exit_race(party_driver, ex=True)
    # print("...Output Value: ", value)

    if "Finished" in value:
      break
    else:
      print_HTML_body(party_driver)
      print_console(party_driver)
      print('..not finished, sleeping a bit..')
      time.sleep(5)
      cnt+=1
      if (cnt==10):
        break
  #while-end

  print_HTML_body(party_driver)
  print_console(party_driver)
  print('...after waiting/while loop')

  exit_race(party_driver, ex=False)

  print('Program output: \n', value, '\n\n')

  # get timers
  timer1 = (value[value.find("Stopped timer 1 at "):]).removeprefix("Stopped timer 1 at ").split(' ', 1)[0]
  timer2 = (value[value.find("Stopped timer 2 at "):]).removeprefix("Stopped timer 2 at ").split(' ', 1)[0]
  timer3 = (value[value.find("Stopped timer 3 at "):]).removeprefix("Stopped timer 3 at ").split(' ', 1)[0]

  # get overall runtime
  runtime = value[value.find("Time = "):]
  runtime = runtime.removeprefix("Time = ")
  runtime = runtime[:6]
  print(runtime)

  # get result
  try:
    result = re.search(r'\n[0-9]+\n', value).group(0).strip()
    print(result)
  except:
    result="null"

  #print Timers
  print("Timer1 (Start-End): ", timer1)
  print("Timer2 (Read Inputs): ", timer2)
  print("Timer3 (Dot Product): ", timer3)

  # print('<b3m4>{"result": %s}</b3m4>' % result)
  # print('<b3m4>{"timer": {"full":%s}       }</b3m4>' % timer1)
  # print('<b3m4>{"timer": {"input":%s}      }</b3m4>' % timer2)
  # print('<b3m4>{"timer": {"inner_prod":%s} }</b3m4>' % timer3)

  print('<b3m4>{"result":%s}</b3m4>' % result)
  print('<b3m4>{"timer":{"full":%s}}</b3m4>' % timer1)
  print('<b3m4>{"timer":{"input":%s}}</b3m4>' % timer2)
  print('<b3m4>{"timer":{"computation":%s}}</b3m4>' % timer3)

  exit(0)


main()