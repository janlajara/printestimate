export const formatNumber = (number, decimalPlaces, fixedDecimal=false) => {
    return number.toLocaleString(undefined, {
        minimumFractionDigits: fixedDecimal ? decimalPlaces : 0,
        maximumFractionDigits: decimalPlaces
    });
}

export const formatQuantity = (quantity, unit_singular, unit_plural) => {
    const number = Number(quantity)
    const formatted = formatNumber(number, 0);
    return `${formatted} ${quantity == 1? unit_singular : unit_plural}`; 
}

export const formatMoney = (amount, currency) => {
    const number = Number(amount)
    const formatted = number.toLocaleString("en-PH", {
        style: 'currency',
        currency: currency,
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });
    return formatted;
}

export const defaultIfNull = (object, defaultValue, property=null) => {
    if (property)
        return object && object[property]? object[property] : defaultValue;
    else
        return object ? object : defaultValue;
}

export const reference = {
    mrs: 'MRS',
    stock: 'STK',
    formatId: (id, code)=> {
        if (id != null && code != null) {
            const padded = Number(id).toString().padStart(5, '0');
            return code + padded
        } else {
            return ''
        }
    },
    getId: (formattedId)=> {
        return formattedId.replace(/[^\d]/g, "");
    }
}