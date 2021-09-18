from os import TMP_MAX, listdir
import xml.etree.ElementTree as ET
from tabulate import tabulate
CFDI3XMLKeysPrefix = '{http://www.sat.gob.mx/cfd/3}'

def main():
    # Get files names
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
        date = root.attrib['Fecha'] # Format: AAAA-MM-DDThh:mm:ss

        subtotalGlobal = float(root.attrib['SubTotal'])
        totalGlobal = float(root.attrib['Total'])
        
        importeImpuesto = 0
        base = 0
        for child in root:
            if(child.tag == CFDI3XMLKeysPrefix + 'Emisor'):
                nombreEmisor = child.attrib['Nombre']
            if(child.tag == CFDI3XMLKeysPrefix + 'Impuestos'):
                totalImpuestoTrasladado = float(child.attrib['TotalImpuestosTrasladados'])

            try:
                if(child.tag == CFDI3XMLKeysPrefix + 'Conceptos'):
                    conceptos = child
                    for concepto in conceptos:
                        if(concepto.tag == CFDI3XMLKeysPrefix + 'Concepto'):
                            impuestos = concepto[0][0]
                            for impuesto in impuestos:
                                impuesto = impuesto.attrib
                                importeImpuestoArticulo = float(impuesto['Importe'])
                                baseArticulo = float(impuesto['Base'])
                                if (impuesto['Impuesto'] == '002'):
                                    if(impuesto['TasaOCuota'] == '0.160000'):
                                        resultTax['Impuestos'] += importeImpuestoArticulo
                                        resultTax['Subtotales'] += baseArticulo
                                    elif(impuesto['TasaOCuota'] == '0.000000'):
                                        print(date + ' ' + currentFile + '' + nombreEmisor)
                                        resultTaxFree['Impuestos'] += importeImpuestoArticulo
                                        resultTaxFree['Subtotales'] += baseArticulo
                                    base += baseArticulo
                                if (impuesto['Impuesto'] == '003'):
                                    resultTax['Impuestos'] += importeImpuestoArticulo
                                importeImpuesto += importeImpuestoArticulo
                                
            except:
                print('Skipping tax calculation of ' + currentFile)
        
        totalCalculado = importeImpuesto + base
        if (abs(totalGlobal - totalCalculado) > 0.1): #tolerancia 10 centavos de error
            diferenciaTotales = totalGlobal - totalCalculado
            print('Incongruencia de $' + str(diferenciaTotales) + ' en la factura ' + currentFile)
            print('SUMANDO '+str(diferenciaTotales)+' a total final CON impuestos (total impuestos)')
            resultTax['Impuestos'] += diferenciaTotales
            # totalGlobal = 0
            # subtotalGlobal = 0
            # totalImpuestoTrasladado = 0
        result['Subtotales'] += subtotalGlobal
        result['Totales'] += totalGlobal
        result['Impuestos'] += totalImpuestoTrasladado

        row = [date, nombreEmisor, subtotalGlobal, totalImpuestoTrasladado, totalGlobal, currentFile]
        data.append(row)
        if (totalImpuestoTrasladado > 0):
            taxData.append(row)
        else:
            taxFreeData.append(row)
    
    print('\n\nResultado total:')
    print(tabulate(data, headers=["Fecha", "Emisor", "SubTotal", "Impuestos", "Total", "Archivo"]))
    print('Resultado total final:')
    finalResult = [list(result.values())]
    print(tabulate(finalResult, headers=["Subtotales", "Total Impuestos", "Total Final"]))

    resultTax['Totales'] += resultTax['Impuestos'] + resultTax['Subtotales']
    print('\n\nResultado facturas CON impuestos: (' + str(len(taxData)) + ')')
    print(tabulate(taxData, headers=["Fecha", "Emisor", "SubTotal", "Impuestos", "Total", "Archivo"]))
    print('Resultado total final CON impuestos:')
    finalResult = [list(resultTax.values())]
    print(tabulate(finalResult, headers=["Subtotales", "Total Impuestos", "Total Final"]))

    resultTaxFree['Totales'] += resultTaxFree['Impuestos'] + resultTaxFree['Subtotales']
    print('\n\nResultado facturas SIN impuestos: (' + str(len(taxFreeData)) + ')')
    print(tabulate(taxFreeData, headers=["Fecha", "Emisor", "SubTotal", "Impuestos", "Total", "Archivo"]))
    print('Resultado total final SIN impuestos:')
    finalResult = [list(resultTaxFree.values())]
    print(tabulate(finalResult, headers=["Subtotales", "Total Impuestos", "Total Final"]))
    

if __name__ == "__main__":
    print("@abrahamharos | ~RIF calculator~")
    print('WARNING: This version only supports Invoices with IVA trasladado\n\n\n\n')

    main()