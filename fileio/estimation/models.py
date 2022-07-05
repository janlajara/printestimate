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

                quantity_count = len(self.order_quantities)
                quantity_start = self.start_col+3
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


    class BillOfMaterialsSection:
        def __init__(self, material_estimates, start_col, start_row):
            self.material_estimates = material_estimates
            self.start_col = start_col
            self.start_row = start_row

        @property
        def rows(self):
            label = ['Bill of Materials']
            header = ['Material', 'Rate']
            materials = []

            for m in self.material_estimates:
                total = [m.name, m.rate.amount, '/ %s' % m.uom]
                stock_needed = ['Stock Needed', '', '']
                spoilage_count = ['Spoilage (10%)', '', '']
                for estimate in m.estimates:
                    total += [estimate.estimated_total_quantity, '']
                    stock_needed += [estimate.estimated_stock_quantity, '']
                    spoilage_count += [estimate.estimated_spoilage_quantity, '']
                materials.extend([total,  stock_needed, spoilage_count])

            return [label, header] + materials

        def write(self, writer, sheet_name):
            dataframe = pd.DataFrame(self.rows)
            dataframe.to_excel(writer, sheet_name=sheet_name, header=False,
                index=False, startcol=self.start_col, startrow=self.start_row)
            self.format(writer, sheet_name)
        
        def format(self, writer, sheet_name):
            workbook = writer.book
            worksheet = writer.sheets[sheet_name]
            if workbook is not None and worksheet is not None:
                pass


    class ServiceEstimatesSection:
        def __init__(self, service_estimates):
            self.service_estimates = service_estimates

    @property
    def header_section(self):
        if self.product_estimate is not None:
            order_quantities = []
            for estimate_quantity in self.product_estimate.estimate_quantities.all():
                order_quantities.append(estimate_quantity.quantity)
            header_section = ProductEstimateSheet.HeaderSection(
                order_quantities, 0, 0)
            return header_section

    @property
    def bill_of_materials_section(self):
        if self.product_estimate is not None:
            material_estimates = self.product_estimate.estimates.material_estimates
            bom_section = ProductEstimateSheet.BillOfMaterialsSection(
                material_estimates, 0, 2)
            return bom_section

    def write(self, writer):
        sheet_name = self.sheet_name
        self.header_section.write(writer, sheet_name)
        self.bill_of_materials_section.write(writer, sheet_name)


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