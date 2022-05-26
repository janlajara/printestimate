import {reactive} from 'vue';
import {roundNumber} from '@/utils/format.js';
import convert from 'convert';

export class ProductComponentHelper {
    constructor(data, meta) { 
        this._state = reactive({
            data, meta
        });
    }

    get finalMaterialDimensions() {
        throw new Error('Implementation required for getter method finalMaterialDimensions.')
    }

    get rawMaterialDimensions(){
        const filtered = this._state.data.material_templates
            // Filter to ensure unique results
            .filter((item, index) => 
                this._state.data.material_templates.findIndex(x=>
                    x.meta_material_option == item.meta_material_option)
                === index);
        let dimensions = [];

        if (filtered && filtered.length > 0)
            dimensions = filtered.map(x => this._getRawMaterialDimension(x));
        return dimensions;
    }

    get machine(){
        const machineOption = this._state.meta.metaMachineOptions.find(x => 
            x.id == this._state.data.machine_option);
        let obj = null;
        if (machineOption) obj = machineOption.machine_obj;
        return obj;
    }

    get targetUom(){
        return this._state.data['size_uom'];
    } 

    get minMaxItemDimensions(){return this.getMinMaxItemDimensions(this.targetUom)}
    get minMaxMachineDimensions(){return this.getMinMaxMachineDimensions(this.targetUom)}

    getMinMaxItemDimensions(targetUom=null) {
        throw new Error('Implementation required for method getMinMaxItemDimensions. Args:', targetUom)
    }
    getMinMaxMachineDimensions(targetUom=null) {
        throw new Error('Implementation required for method getMinMaxMachineDimensions. Args:', targetUom)
    }
    getAttributeMinValue(attributeName) {
        throw new Error('Implementation required for method getAttributeMinValue. Args:', attributeName)
    }
    getAttributeMaxValue(attributeName) {
        throw new Error('Implementation required for method getAttributeMaxValue. Args:', attributeName)
    }
    applyAttributeRules(attributeName, attributeValue, data) {
        throw new Error('Implementation required for method applyAttributeRules. Args:', attributeName, attributeValue, data)
    }

    _getRawMaterialDimension(template){
        throw new Error('Implementation required for method _getRawMaterialDimension. Args', template);
    }

    _getMinMax(arrayOfValues) {
        let min = null;
        let max = null;
        if (arrayOfValues && arrayOfValues.length > 0) {
            min = Math.min.apply(Math, arrayOfValues);
            max = Math.max.apply(Math, arrayOfValues);
        }
        return {min, max}
    }

    static create(materialType, data, meta) {
        let helper = null;

        if (materialType == 'paper') 
            helper = new PaperProductComponentHelper(data, meta);

        return helper;
    }
}


class PaperProductComponentHelper extends ProductComponentHelper {

    get finalMaterialDimensions() {
        const state = this._state;
        return {
            width: state.data['width_value'],
            length: state.data['length_value'],
            uom: state.data['size_uom']}
    }

    _getRawMaterialDimension(template) {
        let dimension = null;
        const metaMaterialOption = 
            this._state.meta.metaMaterialOptions.find(
                y => y.id == template.meta_material_option);
        if (metaMaterialOption) {
            dimension = {
                width: metaMaterialOption.properties.width_value, 
                length: metaMaterialOption.properties.length_value,
                uom: metaMaterialOption.properties.size_uom,
                label: metaMaterialOption.label
            }
        }
        return dimension;
    }

    getMinMaxItemDimensions(targetUom=null) {
        let minMaxDimensions = null;
        const itemDimensions = this.rawMaterialDimensions;
        let uom = null;
        
        if (itemDimensions && itemDimensions.length > 0) {
            const width_values = itemDimensions.map(x => {
                let width = x.width;
                if (targetUom) width = convert(width, x.uom).to(targetUom);
                return width;
            });
            const length_values = itemDimensions.map(x => {
                let length = x.length;
                if (targetUom) length = convert(length, x.uom).to(targetUom);
                return length;
            });
            if (itemDimensions.length > 0) uom = itemDimensions[0].uom;

            minMaxDimensions = {
                width: this._getMinMax(width_values),
                length: this._getMinMax(length_values),
                uom: targetUom || uom
            };
        }

        return minMaxDimensions;
    }

    getMinMaxMachineDimensions(targetUom=null) {
        const machine = this.machine;
        let machineDimensions = null;

        if (machine != null) {
            const uom = machine.uom;
            let minWidth = machine.min_printable_width || machine.min_sheet_width;
            let maxWidth = machine.max_printable_width || machine.max_sheet_width;
            let minLength = machine.min_sheet_length || machine.min_sheet_breakpoint_length;
            let maxLength = machine.max_sheet_length || machine.max_sheet_breakpoint_length;

            if (targetUom) {
                minWidth = convert(minWidth, uom).to(targetUom);
                maxWidth = convert(maxWidth, uom).to(targetUom);
                minLength = convert(minLength, uom).to(targetUom);
                maxLength = convert(maxLength, uom).to(targetUom);
            } 

            machineDimensions = {
                id: machine.id,
                width: {
                    min: minWidth, max: maxWidth},
                length: {
                    min: minLength, max: maxLength},
                uom: uom
            }
        }
        return machineDimensions;
    }

    getAttributeMinValue(attributeName) {
        let min = null;
        if (['width_value', 'length_value'].includes(attributeName) &&
                this.targetUom) {
            min = convert(1, 'inch').to(this.targetUom);
            min = roundNumber(min, 4);
        }
        return min;
    }

    getAttributeMaxValue(attributeName) {
        let max = null;
        if (this.minMaxItemDimensions) {
            const itemWidth = this.minMaxItemDimensions.width.max;
            const itemLength = this.minMaxItemDimensions.length.max;
            const machineWidth = this.machine? 
                this.minMaxMachineDimensions.width.max : null;
                const machineLength = this.machine?
                this.minMaxMachineDimensions.length.max : null;

            if (attributeName == 'width_value') {
                max = this.machine && machineWidth < itemWidth?
                    machineWidth : itemWidth;
            } else if (attributeName == 'length_value') {
                max = this.machine && machineLength < itemLength?
                    machineLength : itemLength;
            }
            if (max) max = roundNumber(max, 4);
        }
        return max;
    }

    applyAttributeRules(attributeName, attributeValue, data) {
        if (attributeName == 'size_uom') {
            // Convert width and length to target unit of measure
            const width_value = data['width_value'] || 
                this.minMaxMachineDimensions.width.max;
            const length_value = data['length_value'] ||
                this.minMaxMachineDimensions.length.max;
            const w = Number(width_value);
            const l = Number(length_value);
            const asIsSizeUom = data['size_uom'] || attributeValue;
            const toBeSizeUom = attributeValue;
            const convertedWidth = convert(w, asIsSizeUom).to(toBeSizeUom);
            const convertedLength = convert(l, asIsSizeUom).to(toBeSizeUom);
            data['width_value'] = roundNumber(convertedWidth, 4); 
            data['length_value'] = roundNumber(convertedLength, 4);
        }
    }
}