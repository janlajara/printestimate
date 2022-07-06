import pandas as pd
from cached_property import cached_property
from fileio.models import ExcelWorkbook


class ProductSummarySheet:
    class GeneralInformationSection:
        def __init__(self, code, name, description, 
                start_row=0, start_col=0):
            self.code = code
            self.name = name
            self.description = description
            self.start_row = start_row
            self.start_col = start_col
        
        @property
        def headers(self):
            return ['Code', 'Product Template', 'Description']

        @property
        def dataframe(self):
            return pd.DataFrame([[self.code], [self.name], [self.description]],
                index=self.headers)

        def write(self, writer, sheet_name):
            self.dataframe.to_excel(writer, sheet_name=sheet_name,
                startcol=self.start_col, startrow=self.start_row,
                header=False)
            self.format(writer, sheet_name)

        def format(self, writer, sheet_name):
            worksheet = writer.sheets[sheet_name]
            if worksheet is not None:
                col_1 = self.start_col + 0
                col_2 = self.start_col + 1
                worksheet.set_column(col_1, col_1, 25)
                worksheet.set_column(col_2, col_2, 30)
    
    class ComponentSection:
        def __init__(self, components, start_row=0, start_col=0):
            self.components = components
            self.start_row = start_row
            self.start_col = start_col

        @property
        def headers(self):
            return ['Component Name', 'Materials', 'Quantity']

        @property
        def dataframe(self):
            return pd.DataFrame(self.rows, columns=self.headers)

        @cached_property
        def rows(self):
            component_rows = []
            for component in self.components:
                row = self.get_row(component)
                if row is not None:
                    component_rows.append(row)
            return component_rows

        def write(self, writer, sheet_name):
            self.dataframe.to_excel(writer, sheet_name=sheet_name, 
                index=False, startcol=self.start_col, startrow=self.start_row)
            self.format(writer, sheet_name)
        
        def format(self, writer, sheet_name):
            workbook = writer.book
            worksheet = writer.sheets[sheet_name]
            if workbook is not None and worksheet is not None:
                textwrap_format = workbook.add_format({'text_wrap': True})
                col_2 = self.start_col + 1
                worksheet.set_column(col_2, col_2, 30, textwrap_format)

                # Increase height of each row with cell containing multi-line breaks
                for (index, component) in enumerate(self.components):
                    material_count = len(component.materials.all()) 
                    if material_count > 1:
                        aligntop_format = workbook.add_format()
                        aligntop_format.set_align('top')
                        row = self.start_row + 1 + index
                        worksheet.set_row(row, material_count * 15, aligntop_format)

        def get_row(self, component):
            if component is not None:
                material_count = len(component.materials.all()) 
                materials = []
                if material_count > 0:
                    materials = [material.label for material 
                        in component.materials.all()]
                joined_materials = "\n".join(materials)

                quantity = ('%s x %s' 
                    % (component.quantity, material_count)
                    if material_count > 1 
                    else component.quantity)

                return [component.name, joined_materials, quantity]

    class ServiceSection:
        def __init__(self, services, start_row=0, start_col=0):
            self.services = services
            self.start_row = start_row
            self.start_col = start_col

        @property
        def headers(self):
            return ['Service Name', 'Application', 'Operation']
        
        @property
        def dataframe(self):
            return pd.DataFrame(self.rows, columns=self.headers)

        @cached_property
        def rows(self):
            service_rows = []
            for service in self.services:
                for operation in service.operation_estimates.all():
                    for (ai, activity) in enumerate(operation.activity_estimates.all()):
                        row = self.get_row(service, operation, activity, ai)
                        if row is not None:
                            service_rows.append(row)
            return service_rows
        
        def get_row(self, service, operation, activity, ai):
            if service is not None and operation is not None and activity is not None:
                service_name = service.name
                action = operation.name
                notes = activity.notes
                step = activity.name + (" " + notes if notes else "")
                if operation.material is not None:
                    action = '%s %s' % (operation.name, operation.material.item.name) 
                return [
                    service_name if ai == 0 else '', 
                    action if ai == 0 else '', step]
        
        def write(self, writer, sheet_name):
            self.dataframe.to_excel(writer, sheet_name=sheet_name, 
                index=False, startcol=self.start_col, startrow=self.start_row)
            self.format(writer, sheet_name)
        
        def format(self, writer, sheet_name):
            workbook = writer.book
            worksheet = writer.sheets[sheet_name]
            if workbook is not None and worksheet is not None:
                col_2 = self.start_col + 2
                worksheet.set_column(col_2, col_2, 30)

    def __init__(self, product_estimate, sheet_name):
        self.product_estimate = product_estimate
        self.sheet_name = sheet_name

    @cached_property
    def product(self):
        if self.product_estimate is not None:
            return self.product_estimate.product

    @cached_property
    def components(self):
        if self.product is not None:
            return self.product.components.all()

    @cached_property
    def services(self):
        if self.product is not None:
            return self.product.services.all()

    @property
    def general_information_section(self):
        if self.product_estimate is not None:
            code = self.product_estimate.estimate_code
            name = self.product_estimate.name
            description = self.product_estimate.description
            return ProductSummarySheet.GeneralInformationSection(
                code, name, description, 0, 0)

    @property
    def component_section(self):
        if self.components is not None:
            return ProductSummarySheet.ComponentSection(
                self.components, 4, 0)

    @property
    def service_section(self):
        if self.services is not None:
            startrow = 4
            if self.component_section is not None:
                startrow += len(self.component_section.rows) + 2
            return ProductSummarySheet.ServiceSection(
                self.services, startrow, 0)

    def write(self, writer):
        sheet_name = self.sheet_name
        self.general_information_section.write(writer, sheet_name)
        self.component_section.write(writer, sheet_name)
        self.service_section.write(writer, sheet_name)


class ProductEstimateSheet:
    def __init__(self, product_estimate, sheet_name):
        self.product_estimate = product_estimate
        self.sheet_name = sheet_name

    class HeaderSection:
        def __init__(self, order_quantities, start_col, start_row):
            self.order_quantities = order_quantities
            self.start_col = start_col
            self.start_row = start_row

        @property
        def header(self):
            return pd.DataFrame([['Cost Breakdown']])

        def write(self, writer, sheet_name):
            self.header.to_excel(writer, sheet_name=sheet_name, header=False,
                index=False, startcol=self.start_col, startrow=self.start_row)
            self.format(writer, sheet_name)
        
        def format(self, writer, sheet_name):
            workbook = writer.book
            worksheet = writer.sheets[sheet_name]
            if workbook is not None and worksheet is not None:
                col_2 = self.start_col
                worksheet.set_column(col_2, col_2, 35)


    class BillOfMaterialsSection:
        def __init__(self, material_estimates, start_col, start_row):
            self.material_estimates = material_estimates
            self.start_col = start_col
            self.start_row = start_row

        @property
        def rows(self):
            header = ['Material', 'Rate', '']
            header_complete = False
            materials = []

            for m in self.material_estimates:
                total = [m.name, m.rate.amount, '/ %s' % m.uom]
                stock_needed = ['Stock Needed', '', '']
                spoilage_count = ['Spoilage (10%)', '', '']
                
                for estimate in m.estimates:
                    if not header_complete:
                        header += ['Qty', 'Cost']
                    total += [estimate.estimated_total_quantity, '']
                    stock_needed += [estimate.estimated_stock_quantity, '']
                    spoilage_count += [estimate.estimated_spoilage_quantity, '']

                if not header_complete:
                    header_complete = True

                materials.extend([total,  stock_needed, spoilage_count])

            return [header] + materials

        def write(self, writer, sheet_name):
            dataframe = pd.DataFrame(self.rows)
            dataframe.to_excel(writer, sheet_name=sheet_name, header=False,
                index=False, startcol=self.start_col, startrow=self.start_row)
            self.format(writer, sheet_name)
            self.set_formulas(writer, sheet_name)
        
        def format(self, writer, sheet_name):
            workbook = writer.book
            worksheet = writer.sheets[sheet_name]
            bold_format = workbook.add_format({'bold': True, 'align': 'center'})

            worksheet.merge_range(2, 1, 2, 2, 'Rate')
            worksheet.set_row(2, None, bold_format)

            indent = workbook.add_format({'indent': 1})

            for (i, m) in enumerate(self.material_estimates):
                row = 3 + (3*i)
                row_val = self.rows
                si = ((i*3)+1)
                worksheet.write(row, 0, row_val[si][0])
                worksheet.write(row+1, 0, row_val[si+1][0], indent)
                worksheet.write(row+2, 0, row_val[si+2][0], indent)

        def set_formulas(self, writer, sheet_name):
            workbook = writer.book
            worksheet = writer.sheets[sheet_name]

            currency_format = workbook.add_format({'num_format': '₱#,##0.00'})
            worksheet.set_column(1, 1, None, currency_format)

            currency_format2 = workbook.add_format(
                {'num_format': '₱#,##0.00', 'right': 1})

            for (i, m) in enumerate(self.material_estimates):
                row = 3 + (3*i)
                for (j, estimate) in enumerate(m.estimates):
                    col = 4 + (2*j)
                    qty_col = str(chr(97+(col-1))).upper()
                    worksheet.write_formula(row, col, 
                        '=B%s*%s%s' % (row+1, qty_col, row+1),
                        currency_format2)

    class ServiceEstimatesSection:
        def __init__(self, service_estimates, start_col, start_row):
            self.service_estimates = service_estimates
            self.start_col = start_col
            self.start_row = start_row

        @property
        def meta(self):
            services = []
            indented = []
            formula = []
            index = 0

            def _add_row(row, indent=None):
                nonlocal index
                services.append(row)
                if indent is not None:
                    indented.append([index, indent, row[0]])
                index += 1
                return index
            
            def _add_formula(row, col, formula_expression):
                formula.append([row, col, formula_expression])
                
            for se in self.service_estimates:
                _add_row([se.name])

                for oe in se.operation_estimates:
                    oeval = [oe.name + 
                        (' ' + oe.item_name if oe.item_name else '')]
                    _add_row(oeval, 1)

                    for ae in oe.activity_estimates:
                        aeval = [ae.name + 
                            (' ' + ae.notes if ae.notes and len(ae.notes) > 0 else '')]
                        _add_row(aeval, 2)

                        for aee in ae.activity_expense_estimates:
                            arr = [aee.name, aee.rate.amount, 
                                aee.type if aee.type == 'flat' else '/ %s' % aee.estimates[0].uom]
                            for (key, estimate) in enumerate(aee.estimates):
                                arr += [1 if aee.type == 'flat' else estimate.quantity, '']
                                row = self.start_row + index + 2
                                col = 4+(2*key)
                                qty_col = str(chr(97+(col-1))).upper()
                                _add_formula(index, col, 
                                    '=B%s*%s%s' % (row, qty_col, row))
                            _add_row(arr, 3)
            return {
                "rows": services,
                "indented": indented,
                "formula": formula}

        @property
        def rows(self):
            header = ['Service']
            services = self.meta.get('rows')
            return [header] + services

        def write(self, writer, sheet_name):
            dataframe = pd.DataFrame(self.rows)
            dataframe.to_excel(writer, sheet_name=sheet_name, header=False,
                index=False, startcol=self.start_col, startrow=self.start_row)
            self.format(writer, sheet_name)

        def format(self, writer, sheet_name):
            workbook = writer.book
            worksheet = writer.sheets[sheet_name]
            bold_format = workbook.add_format({'bold': True, 'align': 'center'})
            worksheet.set_row(self.start_row, None, bold_format)
            currency_format = workbook.add_format({'num_format': '₱#,##0.00', 'right': 1})

            for indented_row in self.meta.get('indented'):
                row_index = self.start_row + 1 + indented_row[0]
                indent_size = indented_row[1]
                value = indented_row[2]
                indent_format = workbook.add_format({'indent': indent_size})
                worksheet.write(row_index, 0, value, indent_format)

            for formula_row in self.meta.get('formula'):
                row = self.start_row + 1 + formula_row[0]
                col = formula_row[1]
                formula = formula_row[2]
                worksheet.write_formula(row, col, formula, currency_format)

    class FooterSection:
        def __init__(self, order_quantities, start_col, start_row):
            self.order_quantities = order_quantities
            self.start_col = start_col
            self.start_row = start_row
        
        @property
        def footer(self):
            return [['Total Price'], ['Unit Price']]
        
        @property
        def meta(self):
            total_prices = []
            unit_prices = []
            sum_start_row = 4
            sum_end_row = self.start_row-1

            for (key, order_quantity) in enumerate(self.order_quantities):
                col = 4+(2*key)
                cost_col = str(chr(97+(col))).upper()
                
                total_price_formula = ('=SUM(%s%s:%s%s)' % 
                    (cost_col, sum_start_row, cost_col, sum_end_row))
                total_prices.append(['%s%s' % (cost_col, self.start_row+1), 
                    total_price_formula])

                unit_price_formula = total_price_formula + ('/%s' % order_quantity)
                unit_prices.append(['%s%s' % (cost_col, self.start_row+2), 
                    unit_price_formula])
            
            return {
                "formula": [total_prices, unit_prices]
            }
        
        def write(self, writer, sheet_name):
            dataframe = pd.DataFrame(self.footer)
            dataframe.to_excel(writer, sheet_name=sheet_name, header=False,
                index=False, startcol=self.start_col, startrow=self.start_row)
            self.format(writer, sheet_name)

        def format(self, writer, sheet_name):
            workbook = writer.book
            worksheet = writer.sheets[sheet_name]
            currency_format = workbook.add_format({'num_format': '₱#,##0.00', 
                'right': 1, 'bold': True, 'underline': True})

            for x in self.meta.get('formula'):
                for formula_row in x:
                    position = formula_row[0]
                    formula_expression = formula_row[1]
                    worksheet.write_formula(position, formula_expression, 
                        cell_format=currency_format)
        
    @property
    def order_quantities(self):
        order_quantities = []
        for estimate_quantity in self.product_estimate.estimate_quantities.all():
            order_quantities.append(estimate_quantity.quantity)
        return order_quantities

    @property
    def header_section(self):
        if self.product_estimate is not None:
            header_section = ProductEstimateSheet.HeaderSection(
                self.order_quantities, 0, 0)
            return header_section

    @property
    def bill_of_materials_section(self):
        if self.product_estimate is not None:
            material_estimates = self.product_estimate.estimates.material_estimates
            bom_section = ProductEstimateSheet.BillOfMaterialsSection(
                material_estimates, 0, 2)
            return bom_section

    @property
    def service_estimates_section(self):
        if self.product_estimate is not None:
            starting_row = len(self.bill_of_materials_section.rows) + 3
            service_estimates = self.product_estimate.estimates.service_estimates
            services_section = ProductEstimateSheet.ServiceEstimatesSection(
                service_estimates, 0, starting_row)
            return services_section

    @property
    def footer_section(self):
        if self.product_estimate is not None:
            starting_row = (len(self.service_estimates_section.rows) +
                len(self.bill_of_materials_section.rows) + 5)
            footer_section = ProductEstimateSheet.FooterSection(
                self.order_quantities, 1, starting_row)
            return footer_section

    def write(self, writer):
        sheet_name = self.sheet_name
        self.header_section.write(writer, sheet_name)
        self.bill_of_materials_section.write(writer, sheet_name)
        self.service_estimates_section.write(writer, sheet_name)
        self.footer_section.write(writer, sheet_name)
        self.format(writer)

    def format(self, writer):
        workbook = writer.book
        worksheet = writer.sheets[self.sheet_name]
        quantity_count = len(self.order_quantities)
        quantity_start = 3
        quantity_format = workbook.add_format({
            'bold': True, 'font_size': 12,
            'align': 'center', 'bottom': 1
        }) 
        columnleft_format = workbook.add_format({'left': 1})
        columnright_format = workbook.add_format({'right': 1})

        for x in range(0, (quantity_count*2)):
            col_idx = quantity_start + x

            if x % 2 == 1:
                idx = int((x-1)/2)
                quantity = self.order_quantities[idx]
                worksheet.merge_range(0, col_idx-1, 0, col_idx, 
                    quantity, quantity_format)
                worksheet.set_column(col_idx, col_idx, 
                    13, columnright_format)
            else:
                worksheet.set_column(col_idx, col_idx, 
                    8, columnleft_format)


class CostEstimateWorkbook(ExcelWorkbook):
    def __init__(self, product_estimate, name='cost-estimate-workbook'):
        self.product_estimate = product_estimate
        self.name = name

    @property
    def sheets(self):
        sheets = []

        if self.product_estimate is not None:
            product_summary_sheet = ProductSummarySheet(
                self.product_estimate, 'Specifications')
            sheets.append(product_summary_sheet)

            product_estimate_sheet = ProductEstimateSheet(
                self.product_estimate, 'Costing')
            sheets.append(product_estimate_sheet)

        return sheets