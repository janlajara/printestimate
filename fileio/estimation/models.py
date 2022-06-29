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
    pass


class CostEstimateWorkbook(ExcelWorkbook):
    def __init__(self, product_estimate, name='cost-estimate-workbook'):
        self.product_estimate = product_estimate
        self.name = name

    @property
    def sheets(self):
        sheets = []

        if self.product_estimate is not None:
            product_estimate_sheet = ProductSummarySheet(
                self.product_estimate, 'Specifications')
            sheets.append(product_estimate_sheet)

        return sheets