import serve

ps = serve.RemotePowerShell("25.84.118.43")
print ps("ls")
