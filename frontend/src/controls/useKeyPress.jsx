import React, { useState } from 'react';
export const useKeyPress = function (targetKey,controlName) {
    const [keyPressed, setKeyPressed] = useState(false);

    React.useEffect(() => {
        const downHandler = ({ key,target }) => {
        
            var ctrlFocus=false;
 

            if(controlName==="none"){
                ctrlFocus=true;   
            }
            else if(target && target.className && target.className.indexOf(controlName) > -1){
                ctrlFocus=true;
            }

            if (ctrlFocus && key === targetKey) {
                setKeyPressed(true);
            }
        }
        const upHandler = ({ key,target }) => {
            var ctrlFocus=false;
            if(controlName==="none"){
                ctrlFocus=true;
            }
            else if(target && target.className && target.className.indexOf(controlName) > -1){
                ctrlFocus=true;
            }
            if (ctrlFocus && key === targetKey) {
                setKeyPressed(false);
            }
        };


        window.addEventListener("keydown", downHandler);
        window.addEventListener("keyup", upHandler);


        return () => {
            window.removeEventListener("keydown", downHandler);
            window.removeEventListener("keyup", upHandler);
        };
    }, [targetKey]);


    return keyPressed;
};
