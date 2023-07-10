import React, { useEffect, useState } from 'react';
import { useKeyPress } from './useKeyPress';
import { grey, randomColor} from '../utils';
import ListItemCtrl from './ListItemCtrl';
import PlusIcon from '../icons/Plus';
import MinusIcon from '../icons/Minus';
import Badge from './Badge';

export default function SearchListCtrl({ options, formats, onItemSelect, selected, showAdd, showRemove, onAddOption, onRemoveOption, onEmptySelection }) {


    const [filteredOptions, setFilteredOptions] = useState(options);

    const [cursor, setCursor] = useState(0);
    const [hovered, setHovered] = useState(undefined);
    const [searchOptionRef, setSearchOptionRef] = useState(null);
    const [selectLabel, setSelectLabel] = useState();
    const [selectValue, setSelectValue] = useState();
    const [showAddOption, setShowAddOption] = useState(false);
    const [showSelect, setShowSelect] = useState(true);
    const [showRemoveOption, setShowRemoveOption] = useState(false);
    const [addSelectRef, setAddSelectRef] = useState(null);
    const [error, setError] = useState();

    const downPress = useKeyPress("ArrowDown", "list-search-input");
    const upPress = useKeyPress("ArrowUp", "list-search-input");
    const enterPress = useKeyPress("Enter", "list-search-input");

    useEffect(() => {
        if (showSelect && filteredOptions.length && downPress) {
            setCursor(prevState =>
                prevState < options.length - 1 ? prevState + 1 : prevState
            );
        }
    }, [downPress]);
    useEffect(() => {
        if (showSelect && filteredOptions.length && upPress) {
            setCursor(prevState => (prevState > 0 ? prevState - 1 : prevState));
        }
    }, [upPress]);
    useEffect(() => {
        if (showSelect && filteredOptions.length && enterPress) {
            if (cursor == undefined) {
                onEmptySelection();
            }
            else {
                onItemSelect(filteredOptions[cursor]);
            }

        }
    }, [cursor, enterPress]);
    useEffect(() => {
        if (filteredOptions.length && hovered) {
            var _index = filteredOptions.findIndex(d => d.value === hovered.value);
            if (_index > -1) {
                setCursor(_index);
            }
        }
    }, [hovered]);

    useEffect(() => {
        if (searchOptionRef) {
            searchOptionRef.focus();
        }
    }, [searchOptionRef]);

    useEffect(() => {

        setFilteredOptions(options)
    }, [options]);

    useEffect(() => {
        if (addSelectRef && showAddOption) {
            addSelectRef.focus();
        }
    }, [addSelectRef, showAddOption]);

    useEffect(() => {
        if (selected) {
            for (var i = 0; i < filteredOptions.length; i++) {
                if (filteredOptions[i].value === selected) {
                    setCursor(i);
                    break;
                }
            }
        }
        else {
            setCursor(undefined);
        }

    }, [selected]);

    function onSearchOptionChange(e) {

        var filtered = [];
        if (e.target.value.length == 0) {
            setCursor(undefined);
            setFilteredOptions(options);
            return;
        }
        if (e.target.value.length > 1) {
            for (var i = 0; i < options.length; i++) {
                if (options[i].label.toLowerCase().indexOf(e.target.value.toLowerCase()) != -1) {
                    filtered.push(options[i]);
                }
            }
        }

        setFilteredOptions(filtered);
        setCursor(0);
    }

    function handleAddOption() {
        setSelectLabel("");
        setSelectValue("");
        setShowSelect(false);
        setShowAddOption(true);
        setShowRemoveOption(false);
    }
    function handleRemoveOption() {
        setShowSelect(true);
        setShowAddOption(false);
        setShowRemoveOption(true);
    }


    function onSelectLabelChange(e) {
        setSelectLabel(e.target.value);
        setSelectValue(e.target.value);

    }
    function onSelectValueChange(e) {
        setSelectValue(e.target.value);
    }

    function getFormat(value) {
        if (formats && formats.hasOwnProperty(value)) {
            return formats[value];
        }
        return null;
    }


    function handleAddSelectOption() {
        setError("");
        if (selectLabel && selectLabel.trim() !== '' && selectValue && selectValue.trim() !== '') {
            var newIndex = options.findIndex(d => d.value === selectValue.trim());

            if (newIndex > -1) {
                setError('Value already exists');
                return;
            }

            var newOption = {
                label: selectLabel.trim(),
                value: selectValue.trim(),
                backgroundColor: randomColor()
            }
            onAddOption(newOption);
            setShowSelect(true);
            setShowAddOption(false);
            setShowRemoveOption(false);
        }
        else {
            setError('Please enter label and value');
        }

    }
    function handleCancelSelectOption() {
        setShowSelect(true);
        setShowAddOption(false);
        setShowRemoveOption(false);
    }

    return (

        <>

            <div>

                {showSelect && <input
                    type="text"
                    className="list-search-input mr-3 mt-3 form-control"
                    placeholder='Find an option'
                    ref={setSearchOptionRef}
                    onChange={onSearchOptionChange}

                />}

                {showAdd && !showAddOption && (<span
                    className="cursor-pointer "

                    onClick={() => handleAddOption()}
                >
                    <Badge
                        value={
                            <span className="svg-icon-sm svg-text" title="Add option">
                                <PlusIcon />
                            </span>
                        }
                        backgroundColor="#eeeeee"
                    />
                </span>)}
                {showAdd && showRemove && (<>&nbsp;</>)}
                {showRemove && !showAddOption && options && options.length > 0 && (<span
                    className="cursor-pointer "

                    onClick={() => handleRemoveOption()}
                >
                    <Badge
                        value={
                            <span className="svg-icon-sm svg-text" simple-title="Remove option">
                                <MinusIcon />
                            </span>
                        }
                        backgroundColor={grey(200)}
                    />
                </span>)}

                {showAddOption && (
                    <>
                        <div
                            className="border-radius-sm"
                            style={{
                                width: 180,
                                padding: '2px 4px',
                            }}
                        >
                            <span className='small-grey-text'>Label </span>   <input
                                type="text"
                                value={selectLabel || ""}
                                className="option-input bg-grey-200"
                                onChange={onSelectLabelChange}

                                ref={setAddSelectRef}
                            />
                            <br />
                            <span className='small-grey-text'>Value </span> <input
                                type="text"
                                value={selectValue || ""}
                                className="option-input bg-grey-200"
                                onChange={onSelectValueChange}


                            />
                            <div className='small-red-text'>{error}</div>
                            <button className='btn save-select-opion-btn' onClick={handleAddSelectOption} >Add</button>
                            <button className='btn save-select-opion-cancel-btn' onClick={handleCancelSelectOption} >Cancel</button>

                        </div>

                    </>


                )}

                <div className='search-list'>
                    {showSelect && filteredOptions.map((option, i) => (
                        <ListItemCtrl
                            key={option.value}
                            active={i === cursor}
                            option={option}
                            format={getFormat(option.value)}
                            setSelected={() => onItemSelect(option)}
                            setHovered={setHovered}
                            remove={showRemoveOption}
                            onRemoveOption={onRemoveOption}
                        />
                    ))}
                </div>


            </div>
        </>

    )
}



