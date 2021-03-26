
export const formatQuantity = (quantity, unit_singular, unit_plural) => {
    const number = Number(quantity)
    const formatted = number.toLocaleString(undefined, {
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    });
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

export const assignValue = (value, defaultValue) => {
    return value ? value : defaultValue;
}