import React from 'react';

export default function Badge({ value, backgroundColor, capitalize, color }) {
  return (
    <span
      className={capitalize ? "font-weight-400 d-inline-block color-grey-800 border-radius-sm text-transform-capitalize"
        : "font-weight-400 d-inline-block color-grey-800 border-radius-sm"}
      style={{
        backgroundColor: backgroundColor,
        padding: '2px 6px',
        color: color ? color : "#424242"
      }}
    >
      {value}
    </span>
  );
}
