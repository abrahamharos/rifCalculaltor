from os import TMP_MAX, listdir
import xml.etree.ElementTree as ET
from tabulate import tabulate
CFDI3XMLKeysPrefix = '{http://www.sat.gob.mx/cfd/3}'

def main():
    invoices = [_ for _ in listdir('invoices/') if _.endswith(r".xml")]
    print('Total de archivos leidos:\t', len(invoices))
    taxFreeData = []
    resultTaxFree = {'Subtotales': 0.0, 'Impuestos': 0.0, 'Totales':0.0}
    taxData = []
    resultTax = {'Subtotales': 0.0, 'Impuestos': 0.0, 'Totales':0.0}
    data = []
    result = {'Subtotales': 0.0, 'Impuestos': 0.0, 'Totales':0.0}
    for i in range(0, len(invoices)):
        currentFile = invoices[i]
        tree = ET.parse('invoices/' + currentFile)
        root = tree.getroot()

        subtotal = float(root.attrib['SubTotal'])

        total = float(root.attrib['Total'])
        

        date = root.attrib['Fecha'] # Format: AAAA-MM-DDThh:mm:ss

        # In case of a present discount
        try:
            descuento = float(root.attrib['Descuento'])
        except:
            descuento = 0

        for child in root:
            if(child.tag == CFDI3XMLKeysPrefix + 'Emisor'):
                nombreEmisor = child.attrib['Nombre']
            if(child.tag == CFDI3XMLKeysPrefix + 'Impuestos'):
                totalImpuestoTrasladado = float(child.attrib['TotalImpuestosTrasladados'])

        totalCalculado = totalImpuestoTrasladado + subtotal - descuento
        if (total/10000 < abs(total - totalCalculado)): #tolerancia 0.01% de error
            print('Incongruencia de $' + str(total - totalCalculado) + ' en la factura ' + currentFile)
            total = 0
            subtotal = 0
            totalImpuestoTrasladado = 0
        result['Subtotales'] += subtotal
        result['Totales'] += total
        result['Impuestos'] += totalImpuestoTrasladado

        row = [date, nombreEmisor, subtotal, totalImpuestoTrasladado, total, currentFile]
        data.append(row)
        if (totalImpuestoTrasladado > 0):
            taxData.append(row)
            resultTax['Subtotales'] += subtotal
            resultTax['Totales'] += total
            resultTax['Impuestos'] += totalImpuestoTrasladado
        else:
            taxFreeData.append(row)
            resultTaxFree['Subtotales'] += subtotal
            resultTaxFree['Totales'] += total
            resultTaxFree['Impuestos'] += totalImpuestoTrasladado
    
    print('\n\nResultado total:')
    print(tabulate(data, headers=["Fecha", "Emisor", "SubTotal", "Impuestos", "Total", "Archivo"]))
    print('Resultado total final:')
    finalResult = [list(result.values())]
    print(tabulate(finalResult, headers=["Subtotales", "Total Impuestos", "Total Final"]))

    print('\n\nResultado facturas CON impuestos: (' + str(len(taxData)) + ')')
    print(tabulate(taxData, headers=["Fecha", "Emisor", "SubTotal", "Impuestos", "Total", "Archivo"]))
    print('Resultado total final CON impuestos:')
    finalResult = [list(resultTax.values())]
    print(tabulate(finalResult, headers=["Subtotales", "Total Impuestos", "Total Final"]))

    print('\n\nResultado facturas SIN impuestos: (' + str(len(taxFreeData)) + ')')
    print(tabulate(taxFreeData, headers=["Fecha", "Emisor", "SubTotal", "Impuestos", "Total", "Archivo"]))
    print('Resultado total final SIN impuestos:')
    finalResult = [list(resultTaxFree.values())]
    print(tabulate(finalResult, headers=["Subtotales", "Total Impuestos", "Total Final"]))
    

if __name__ == "__main__":
    print("@abrahamharos | ~RIF calculator~")
    print('WARNING: This version only supports Invoices with IVA trasladado\n\n\n\n')

    main()