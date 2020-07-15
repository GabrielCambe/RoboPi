from datetime import datetime
from pytz import timezone

actualDate = datetime.now()
timeZone = timezone('America/Sao_Paulo')
actualDateSP = timeZone.localize(actualDate)
actualDateSPtext = actualDateSP.strftime('_%d-%m-%Y_%H-%M-%S')

print(actualDateSPtext)
print(((timezone('America/Sao_Paulo')).localize(datetime.now())).strftime('_%d-%m-%Y_%H-%M-%S'))
