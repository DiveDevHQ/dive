import React, { useEffect, useState } from 'react';
import Badge from './Badge';
import Trash from '../icons/Trash';

export default function ListItemCtrl({ option, format, active, setSelected, setHovered, remove, onRemoveOption }) {

    return (
        <>


            <div

                className={`item ${active ? "list-item-hover cursor-pointer mr-4 mt-4" : " cursor-pointer mr-4 mt-4"}`}
                onClick={() => setSelected(option)}
                onMouseEnter={() => setHovered(option)}
                onMouseLeave={() => setHovered(undefined)}
            >
                {option.title && (<span className='filter-parent-text'>{option.title}</span>)}
                <Badge
                    value={option.label}
                    backgroundColor={format && format.backgroundColor ? format.backgroundColor : option.backgroundColor}
                    color={format && format.color ? format.color : option.color}
                />

                {remove && option.value && (<span className="svg-icon-sm svg-text" title="Remove option"
                    onClick={() => onRemoveOption(option)}>
                    &nbsp; <Trash />
                </span>)}
            </div>
        </>

    )
}