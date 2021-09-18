from os import listdir
import xml.etree.ElementTree as ET
from tabulate import tabulate
CFDI3Prefix = '{http://www.sat.gob.mx/cfd/3}'

def main():
    invoices = listdir('invoices/')
    data = []
    result = {'Subtotales': 0.0, 'Impuestos': 0.0, 'Totales':0.0}
    for i in range(0, len(invoices)):
        currentFile = invoices[i]
        tree = ET.parse('invoices/' + currentFile)
        root = tree.getroot()

        subtotal = float(root.attrib['SubTotal'])
        result['Subtotales'] += subtotal

        total = float(root.attrib['Total'])
        result['Totales'] += total

        date = root.attrib['Fecha'] # Format: AAAA-MM-DDThh:mm:ss

        for child in root:
            if(child.tag == CFDI3Prefix + 'Emisor'):
                nombreEmisor = child.attrib['Nombre']
            if(child.tag == CFDI3Prefix + 'Impuestos'):
                totalImpuestoTrasladado = float(child.attrib['TotalImpuestosTrasladados'])

        if (total != (totalImpuestoTrasladado + subtotal)):
            total = 0
            subtotal = 0
            totalImpuestoTrasladado = 0
        
        result['Impuestos'] += totalImpuestoTrasladado
        row = [date, nombreEmisor, subtotal, totalImpuestoTrasladado, total]
        data.append(row)

    print(tabulate(data, headers=["Fecha", "Emisor", "SubTotal", "Impuestos", "Total"]))
    print('\n\Resultado final:')
    
    finalResult = [list(result.values())]
    print(tabulate(finalResult, headers=["Total Impuestos", "Subtotales", "Total Final"]))
    


if __name__ == "__main__":
    print("@abrahamharos | ~RIF calculator~")
    print('WARNING: This version only supports Invoices with IVA trasladado\n\n\n\n')

    main()