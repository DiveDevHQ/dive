import React from "react"
import PropTypes from "prop-types"

const FileProgress = ({percentage}) => {
	return (
		<div className="progress">
			<div
        className="progress-bar progress-bar-striped bg-success"
        role="progressbar"
        style={{ width: `${percentage}%` }}
      >
      { percentage }%
      </div>
		</div>
	);
};

FileProgress.propTypes = {
	percentage: PropTypes.number.isRequired
}

export default FileProgress