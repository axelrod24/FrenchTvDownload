import React, { Component } from 'react';


const Item = ({classname, value, style}) => <td className={classname} style={style}>{value}</td>

class Row extends Component {

    render() {
        var thecolor = "green"
        return ( 
            <tr>
                <Item value={this.props.index + 1} />
                <Item classname="url" value={this.props.data.url} />
                <Item />
                <Item value={this.props.data.status} style={{color: thecolor}}/>
            </tr>
        )
    }
}

class UrlTable extends Component {
    constructor(props) {
        super(props) ;
        this.status = { 
            update: false,
            data: this.props.data
        }
    }

    render() {
        return (
            <div className="people">
                <table>
                    <caption>List of Url</caption>
                    <thead>
                        <tr>
                            <th>url</th>
                            <th>status</th>
                            <th>timestamp</th>
                            <th>action</th>
                        </tr>
                    </thead>
                    <tbody>
                        {this.status.data.map((data, index) => <Row data={data} index={index}/>)}
                    </tbody>
                </table>
            </div> 
        )
    }
}

export default UrlTable ;
