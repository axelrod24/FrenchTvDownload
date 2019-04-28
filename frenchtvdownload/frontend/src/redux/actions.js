
function UrlAction(state = { data: []}, action) {
  switch (action.type) {
    case "ADD_URL":
      state.data.push(action.payload)
      state.data.sort((a, b) => {
        if (a.timestamp > b.timestamp) return -1
        if (a.timestamp < b.timestamp) return 1
        return 0
      })
      return {...state, data: [...state.data]}

    case "REPLACE_URL":
      return {...state, 
        data: state.data.map((v, index) => (v.uid === action.payload.uid) ? action.payload : v) }

    case "SHOW_ALL":
      return {...state}

    case "UPDATE_STATUS":
      return {...state, 
        data: state.data.map((v, index) => (v.uid === action.payload.id) ? (v => {v.status=action.payload.status ; return v})(v) : v) }
    
    case "UPDATE_MDATA":
    return {...state, 
      data: state.data.map((v, index) => (v.uid === action.payload.id) ? (v => {v.metadata=Object.assign(v.metadata, action.payload.mdata) ; return v})(v) : v) }
  
    case "REMOVE_URL":
      return {...state, data: state.data.filter(v => (v.uid !== action.payload))}

    default:
      return {...state}
  }
}

export default UrlAction
