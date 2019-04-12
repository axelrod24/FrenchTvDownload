
function UrlAction(state = { data: []}, action) {
  switch (action.type) {
    case "ADD_URL":
      return {...state, data: [...state.data, action.payload]}

    case "REPLACE_URL":
      // return {...state, data: [...state.data, action.payload]}
      return {...state, 
        data: state.data.map((v, index) => (v.uid === action.payload.uid) ? action.payload : v) }

    case "SHOW_ALL":
      return {...state}

    case "UPDATE_STATUS":
      return {...state, 
        data: state.data.map((v, index) => (v.uid === action.payload.id) ? (v => {v.status=action.payload.status ; return v})(v) : v) }
    case "REMOVE_URL":
    return {...state, data: state.data.filter(v => (v.uid != action.payload))}
    defaut:
      return {...state}
  }
}

export default UrlAction
