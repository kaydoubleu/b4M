from mpyc.runtime import mpc

async def main():
  await mpc.start()
  print('<b3m4>...modified test program :D</b3m4>')
  print('<b3m4>...another one bytes the bits :b</b3m4>')
  print('<b3m4>...test3</b3m4>')
  print('<b3m4>..."test4"</b3m4>')
  print('plain b3m4 :D')
  await mpc.shutdown()

if __name__ == '__main__':
  mpc.run(main())
