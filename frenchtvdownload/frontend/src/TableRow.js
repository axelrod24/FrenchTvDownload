import React, { Component } from 'react';

const Item = ({classname, value, style}) => <td className={classname} style={style}>{value}</td>
const Button = ({classname, value, style, onClick}) => <button className={classname} style={style} onClick={onClick}>{value}</button>
const ButtonItem = ({classname, value, style, onClick}) => <Item className={classname} style={style} value={<button> onClick={onClick}>{value}</button>} />

const MetaDataTable = ({data}) => {
                    return (
                          <table className="matadata-table">
                            <tr>
                              <td style={{width: "80px"}}>Title:</td><td>{data.metadata.progTitle}</td>
                            </tr>
                            <tr>
                              <td>Name:</td><td>{data.metadata.progName}</td>
                            </tr>
                            <tr>
                              <td>Synopsis:</td><td>{data.metadata.synopsis}</td>
                            </tr>
                            <tr>
                              <td>Filename:</td><td>{data.metadata.filename}</td>
                            </tr>
                            <tr>
                              <td>Manifest:</td><td><a href={data.metadata.manifest}>{data.metadata.manifest}</a></td>
                            </tr>
                          </table>
                          ) 
                  }

class TableRow extends Component {
    constructor(props) {
        super(props) ;
        this.state = {
            status: this.props.data.status,
            showMetadata: false
        }

        this.onDownloadVideo = this.onDownloadVideo.bind(this)
        this.onCancelDownload = this.onCancelDownload.bind(this)
        this.onClick = this.onClick.bind(this)
    }

    render() {

        var statusText, statusBgColor ;

        switch(this.state.status) {
            case "done":
                statusText = "Done" 
                statusBgColor = "Aquamarine" 
            break ;

            case "pending":
                statusText = "Pending"
                statusBgColor = "CornflowerBlue"
            break ;

            case "downloading":
                statusText = "..."
                statusBgColor = "Plum"
            break ;
            
            case "not_availabl":
                statusText = "Not Available"
                statusBgColor = "greenyellow"
            break ;

            default:
                statusText = "Unknown"
                statusBgColor = "red"
            break ;
        }

        return ( 
          <tr>
            <Item value={this.props.data.uid} />
            <td className="url" onClick={this.onClick}>
              <div>{this.props.data.url}</div>
              {(this.state.showMetadata) ? <MetaDataTable data={this.props.data} /> : null}
            </td>
            <Item value={this.props.data.timestamp}/>
            <Item value={statusText} style={{background: statusBgColor}}/>
            <td>
                {(this.state.status==="downloading") ? 
                    <Button value="Cancel" onClick={this.onCancelDownload}/> : <Button value="Remove" onClick={() => this.props.onRemoveUrl(this.props.index)}/>}
                {(this.state.status==="pending") && <Button value="Download" onClick={this.onDownloadVideo}/>}
            </td>
          </tr>
        )
    }

    onDownloadVideo() {
        console.log("onDownloadVideo:",this.props.index)
    }

    onCancelDownload() {
        console.log("onCancelDownload:",this.props.index)
    }

    onClick() {
      this.setState({showMetadata: !this.state.showMetadata})
    }
}

export default TableRow ;

