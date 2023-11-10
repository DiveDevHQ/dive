import Cookie from 'universal-cookie';

export function randomColor() {
    return `hsl(${Math.floor(Math.random() * 360)}, 95%, 90%)`;
  }
  
  export function grey(value) {
    let reference = {
      50: '#fafafa',
      100: '#f5f5f5',
      200: '#eeeeee',
      300: '#e0e0e0',
      400: '#bdbdbd',
      500: '#9e9e9e',
      600: '#757575',
      700: '#616161',
      800: '#424242',
      900: '#212121',
    };
  
    return reference[value];
  }
  

 
  export function generateUUID() {
    return ([1e7] + -1e3 + -4e3 + -8e3 + -1e11).replace(/[018]/g, c =>
      (c ^ crypto.getRandomValues(new Uint8Array(1))[0] & 15 >> c / 4).toString(16)
    );
  
  }
  

export function getUserId() {
  var cookie = new Cookie();
  var access_token = cookie.get('user_id');
  return access_token;
}


export function getAccessToken() {
  var cookie = new Cookie();
  var access_token = cookie.get('access_token');
  return access_token;
}


export function clearCookie() {
  var cookie = new Cookie();
  cookie.remove('access_token');
}



export default function saveAccessToken(accessToken) {
  var cookie = new Cookie();
  cookie.set('access_token', accessToken, {
    path: '/', httpOnly: false,
    maxAge: 365 * 24 * 60 * 60 * 1000
  });
}