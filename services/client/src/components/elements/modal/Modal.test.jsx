import React from 'react'
import { configure, shallow} from 'enzyme'

import Modal from '.'

// TODO: (arvy@neuraldev.io) -- might add more complex tests later on. 

const mockFn = jest.fn()

//  Snapshot test
describe('<Modal/>', () => {
  //Make sure it has been rendered
  it('renders <ReactModal>', () => {
    const wrapper = shallow(<Modal show={true} handleClick = {mockFn} />)
    expect(wrapper.length).toEqual(1)
  })
  //Make sure that its rendered correctly
  it('should render correctly', () => {
    const wrapper = shallow(<Modal show={true}>This works</Modal>)
    expect(wrapper).toMatchSnapshot()
  })
  //Make sure that it renders the children correctly
  it('renders children correctly', () => {
    const wrapper = shallow(<Modal show={true} handleClick = {mockFn}>It works</Modal>)
    expect(wrapper.text()).toEqual('It works')
  })
})