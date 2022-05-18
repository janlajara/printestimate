import {reactive} from 'vue';
import {roundNumber} from '@/utils/format.js';
import convert from 'convert';

export class ProductComponentHelper {
    constructor(rawMaterialDimensions, machine, targetUom) {
        this._state = reactive({
            rawMaterialDimensions, machine, targetUom
        })
    }

    set rawMaterialDimensions(value){this._state.rawMaterialDimensions = value}
    get rawMaterialDimensions(){return this._state.rawMaterialDimensions}

    set machine(value){this._state.machine = value}
    get machine(){return this._state.machine}

    set targetUom(value){this._state.targetUom = value}
    get targetUom(){return this._state.targetUom} 

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

    _getMinMax(arrayOfValues) {
        let min = null;
        let max = null;
        if (arrayOfValues && arrayOfValues.length > 0) {
            min = Math.min.apply(Math, arrayOfValues);
            max = Math.max.apply(Math, arrayOfValues);
        }
        return {min, max}
    }

    static create(materialType, rawMaterialDimensions, machine=null, targetUom=null) {
        let helper = null;

        if (materialType == 'paper') 
            helper = new PaperProductComponentHelper(rawMaterialDimensions, machine, targetUom);

        return helper;
    }
}


class PaperProductComponentHelper extends ProductComponentHelper {

    getMinMaxItemDimensions(targetUom=null) {
        const itemDimensions = this.rawMaterialDimensions;
        let uom = null;
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

        return {
            width: this._getMinMax(width_values),
            length: this._getMinMax(length_values),
            uom: targetUom || uom
        }
    }

    getMinMaxMachineDimensions(targetUom=null) {
        const machine = this.machine;
        let machineDimensions = null;

        if (machine != null) {
            const uom = machine.uom;
            let minWidth = machine.min_sheet_width;
            let maxWidth = machine.max_sheet_width;
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
        if (['width_value', 'length_value'].includes(attributeName)) {
            min = convert(1, 'inch').to(this.targetUom);
            min = roundNumber(min, 4);
        }
        return min;
    }

    getAttributeMaxValue(attributeName) {
        let max = null;
        if (attributeName == 'width_value') {
            max = this.machine && this.minMaxMachineDimensions.width.max <
                    this.minMaxItemDimensions.width.max?
                this.minMaxMachineDimensions.width.max : 
                this.minMaxItemDimensions.width.max;
        } else if (attributeName == 'length_value') {
            max = this.machine && this.minMaxMachineDimensions.length.max < 
                    this.minMaxItemDimensions.length.max?
                this.minMaxMachineDimensions.length.max : 
                this.minMaxItemDimensions.length.max;
        }
        if (max) max = roundNumber(max, 4);
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