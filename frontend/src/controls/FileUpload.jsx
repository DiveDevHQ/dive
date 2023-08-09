import React, { Fragment, useState } from 'react';
import FileMessage from './FileMessage';
import FileProgress from './FileProgress';
import { generateUUID, uploadFile } from '../utils';
import { createClient } from '@supabase/supabase-js'
import { addTemplate, authWithPublicData } from '../api';

const FileUpload = ({ fileType, account_id, onUploadFile }) => {
  const [file, setFile] = useState('');
  const [filename, setFilename] = useState('Choose File');
  const [uploadedFile, setUploadedFile] = useState({});
  const [message, setMessage] = useState('');
  const [uploadPercentage, setUploadPercentage] = useState(0);
  const [error, setError] = useState();

  const onChange = e => {
    setFile(e.target.files[0]);
    setFilename(e.target.files[0].name);
  };

  const onSubmit = async e => {
    e.preventDefault();
    const formData = new FormData();
    formData.append('file', file);

    try {

      const supabase = createClient(process.env.REACT_APP_SUPABASE_CLIENT, process.env.REACT_APP_SUPABASE_ANON_KEY)


      const { data, error } = await supabase.storage
        .from('files/user_files')
        .upload(generateUUID() + '_' + filename, file);

      if (error) {
        setError('Upload failed. Please try again!');
      }
      else {
        setError('')
        setUploadPercentage(80);
        var path = data.path;
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
          setUploadPercentage(90);
          var schema = { 'name': schema_name, 'file_url': path, 'mime_type': mime_type };
          addTemplate('upload', 'filestorage', schema_name, schema, account_id, chunking_type).then(data => {
            setUploadPercentage(100);
            onUploadFile();
          });

        })
      }

      /*const res = await axios.post('/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        },
        onUploadProgress: progressEvent => {
          setUploadPercentage(parseInt(Math.round((progressEvent.loaded * 100) / progressEvent.total)));
          setTimeout(() => setUploadPercentage(0), 10000);
        }
      });*/


    } catch (err) {
      if (err.response.status === 500) {
        setMessage('There was a problem witht he server');
      } else {
        setMessage(err.response.data.msg);
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