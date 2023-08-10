import React, { Fragment, useState } from 'react';
import FileMessage from './FileMessage';
import FileProgress from './FileProgress';
import { generateUUID, uploadFile } from '../utils';
import { createClient } from '@supabase/supabase-js'
import { addTemplate, authWithPublicData } from '../api';
import axios from 'axios';

const FileUpload = ({ fileType, account_id, onUploadFile }) => {
  const [file, setFile] = useState('');
  const [filename, setFilename] = useState('Choose File');
  const [uploadedFile, setUploadedFile] = useState({});
  const [message, setMessage] = useState('');
  const [uploadPercentage, setUploadPercentage] = useState(0);
  const [error, setError] = useState();

  const onChange = e => {
    if (e.target.files && e.target.files.length > 0) {
      setFile(e.target.files[0]);
      if (e.target.files[0]) {
        setFilename(e.target.files[0].name);
      }
    }

  };

  const onSubmit = async e => {
    e.preventDefault();
    var unique_filename = generateUUID() + '_' + filename;
    const formData = new FormData();
    formData.append('file', file);
    formData.append('account_id', account_id);
    formData.append('file_name', unique_filename);


    try {

      const res = await axios.post(`${process.env.REACT_APP_API_URL}/file/upload`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        },
        onUploadProgress: progressEvent => {
          setUploadPercentage(parseInt(Math.round((progressEvent.loaded * 100) / progressEvent.total)));
          setTimeout(() => setUploadPercentage(0), 10000);
        }
      });

      authWithPublicData('upload', account_id).then(data => {
        var chunking_type = { 'chunking_type': 'custom' };
        var schema_name = filename;
        var mime_type = '';
        if (filename.indexOf('.') > -1) {
          schema_name = filename.split('.')[0];
          mime_type = filename.split('.')[1];
          if (fileType === 'deck' && mime_type == 'pdf') {
            mime_type = 'pdf_image';
          }
        }
        var schema = { 'name': schema_name, 'file_url': account_id + '/' + unique_filename, 'mime_type': mime_type };
        addTemplate('upload', 'filestorage', schema_name, schema, account_id, chunking_type).then(data => {
          onUploadFile();
        });

      })

    } catch (err) {
      if (err.response.status === 500) {
        setError('Upload failed. Please try again!');
      } else {
        setError(err.response.data.msg);
      }
    }
  }

  return (
    <Fragment>
      {message ? <FileMessage msg={message} /> : null}
      <form onSubmit={onSubmit}>
        <div className="custom-file mb-4">
          <input
            type="file"
            className="custom-file-input"
            id="customFile"
            onChange={onChange}
          />
          <label className='custom-file-label' htmlFor='customFile'>
            {filename}
          </label>
        </div>

        <FileProgress percentage={uploadPercentage} />

        <input
          type="submit"
          value="Upload"
          className="btn btn-blue btn-block mt-4"
        />
        <span className='red-text fr mt-3'>{error}</span>
      </form>
      {uploadedFile ? <div className="row mt-5">
        <div className="col-md-6 m-auto"></div>
        <h3 className="text-center">{uploadedFile.fileName}</h3>
        <img style={{ width: '100%' }} src={uploadedFile.filePath} alt="" />
      </div> : null}
    </Fragment>
  );
};

export default FileUpload;