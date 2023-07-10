import React, { useEffect, useState } from 'react';
import Badge from './Badge';
import { usePopper } from 'react-popper';
import SearchListCtrl from './SearchListCtrl';
import TriangleEmptyDownIcon from '../icons/TriangleEmptyDownIcon';
export default function SelectCtrl({ dataSource, label, id, onSelectChange, selectedValue }) {

    const [filterField, setFilterField] = useState({});
    const [allData, setAllData] = useState([]);
    const [showSelect, setShowSelect] = useState(false);
    const [showFilter, setShowFilter] = useState(false);
    const [selectRef, setSelectRef] = useState(null);
    const [selectPop, setSelectPop] = useState(null);

    const [addSearchFieldRef, setSearchFieldRef] = useState(null);
    const [addSearchSelectRef, setSearchSelectRef] = useState(null);
    const { styles, attributes } = usePopper(selectRef, selectPop, {
        placement: 'bottom-start',
        strategy: 'fixed',
    });


    useEffect(() => {
        if (dataSource) {
            setAllData(dataSource);

        }
        if (dataSource && selectedValue) {
            var selectIndex = dataSource.findIndex(d => d.value === selectedValue);
            if (selectIndex > -1) {

                setFilterField(dataSource[selectIndex]);
            }
        }
        if(!selectedValue){
            setFilterField(null);
        }
        

    }, [dataSource, selectedValue]);

    function handleOptionClick(option) {
        setFilterField(option);
        setShowSelect(false);
        onSelectChange(id, option.text, option.value);
    }

    function handleEmptySelection() {
        const timeout = setTimeout(() => {
            setShowSelect(false);
        }, 100);
    }


    useEffect(() => {
        if (addSearchFieldRef && showSelect) {
            addSearchFieldRef.focus();
        }
    }, [addSearchFieldRef, showSelect]);

    return (
        <>
            <div

            >

                <>
                    <div
                        className='filter-select'
                        ref={setSelectRef}
                        onClick={() => {
                            setShowSelect(true);

                        }
                        }

                    >
                        {filterField && filterField.label ? <>
                            <Badge value={filterField.label} />
                        </> : <span className='text-placeholder'>{label}</span>}
                        <span
                            className="svg-icon-xm svg-light-gray fr"
                        >
                            <TriangleEmptyDownIcon /></span>
                    </div>

                    {showSelect && (
                        <div className="overlay" onClick={() => setShowSelect(false)} />
                    )}
                    {showSelect &&
                        (
                            <div
                                className="shadow-5 bg-white border-radius-md"
                                ref={setSelectPop}
                                {...attributes.popper}
                                style={{
                                    ...styles.popper,
                                    zIndex: 4,
                                    minWidth: 200,
                                    maxWidth: 350,
                                    maxHeight: 300,
                                    padding: '0.75rem',
                                    overflow: 'auto',
                                }}
                            >
                                <div
                                    className="d-flex flex-wrap-wrap "
                                    style={{ marginTop: '0.1rem', width: 250 }}
                                >
                                    {
                                        <>
                                            <SearchListCtrl options={allData} onItemSelect={handleOptionClick} selected={filterField ? filterField.value : null} showAdd={false} showRemove={false}
                                                onAddOption={null} onRemoveOption={null} onEmptySelection={handleEmptySelection}
                                            />

                                        </>

                                    }

                                </div>
                            </div>

                        )}

                </>
            </div>
        </>
    )

}