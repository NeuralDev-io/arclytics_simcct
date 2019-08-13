import React, { Component } from 'react'
import { connect } from 'react-redux'
import { createUserProfile } from '../../../state/ducks/persist/actions'
import Select from '../../elements/select'
import Button from '../../elements/button'

import styles from './ProfileQuestions.module.scss'

import Modal from '../../elements/modal'

class ProfileQuestions extends Component{
  constructor(props){
    super(props)
    this.state = {
      question1: null,
      question1Select: [
        { label: 'To defeat the huns', value: 'To defeat the huns'},
        { label: 'Option 2', value: 'opt12'},
      ],
      question2: null,
      question2Select: [
        { label: 'Be a man training montage', value: 'Be a man training montage'},
        { label: 'Option 2', value: 'opt22'},
      ],
      question3: null,
      question3Select: [
        { label: 'Swords', value: 'Swords'},
        { label: 'Option 2', value: 'opt32'},
      ],
      question4: null,
      question4Select: [
        { label: 'Fireworks', value: 'Fireworks'},
        { label: 'Option 2', value: 'opt42'},
      ],
      showQuestions: true
    }
  }

  handleSubmit = () => {
    const { question1, question2, question3, question4 } = this.state
    // console.log(question1.value, question2.value, question3.value, question4.value)
    this.props.createUserProfileConnect({ 
        aim: question1.label, 
        highest_education: question2.label, 
        sci_tech_exp: question3.label, 
        phase_transform_exp: question4.label
    })
    this.setState({showQuestions: false}) 
  }

  handleSkip = () => {
    this.state.showQuestions ? this.setState({showQuestions: false}) : this.setState({showQuestions: true})
  }

  handleChange = (name, value) => {
    this.setState({
      [name]: value
    })
  }

  render(){
    const { 
      question1, question1Select, 
      question2, question2Select, 
      question3, question3Select,
      question4, question4Select,
      showQuestions} = this.state
    const { profile } = this.props
    return(
      <Modal clicked={this.handleSkip} className={styles.modalQuestions} show={!profile && showQuestions}>
        <div className={styles.content}>
          <div className={styles.header}>
            <h3>More about you...</h3>
            Help us understand our user
          </div>

        <div className={styles.questions}>
          <div className={styles.question}>
            <h6 className={styles.questionText}> What sentence best describes you? </h6>
            <Select
              type="question1"
              name="question1"
              placeholder="---"
              value= {question1}
              options={question1Select}
              length="stretch"
              onChange={value => this.handleChange('question1', value )}
            />
          </div>

          <div className={styles.question}>
            <h6 className={styles.questionText}> What is the highest level of education have you studied? </h6>
            <Select
              type="question2"
              name="question2"
              placeholder="---"
              value= {question2}
              options={question2Select}
              length="stretch"
              onChange={value => this.handleChange('question2', value )}
            />
          </div>

          <div className={styles.question}>
            <h6 className={styles.questionText}>What is your experience with solid-state phase transformation?</h6>
            <Select
              type="question3"
              name="question3"
              placeholder="---"
              value= {question3}
              options={question3Select}
              length="stretch"
              onChange={value => this.handleChange('question3', value )}
            />
          </div>

          <div className={styles.question}>
            <h6 className={styles.questionText}> What is your experience with scientific software? </h6>
            <Select
              type="question4"
              name="question4"
              placeholder="---"
              value= {question4}
              options={question4Select}
              length="stretch"
              onChange={value => this.handleChange('question4', value)}
            />
          </div>
        </div>
        <div className={styles.buttons}>
            <Button classname={styles.skip} appearance="outline" onClick={this.handleSkip}> SKIP </Button>
            <Button className={styles.send} isDisabled={!(question1 && question2 && question3 && question4)} onClick={this.handleSubmit} > SEND </Button>
        </div>
      </div>
    </Modal>
    )
    
  }
}

//TODO: proptypes

const mapStateToProps = state => ({
  profile: state.persist.user.profile
})

const mapDispatchToProps = {
  createUserProfileConnect: createUserProfile,
}

export default connect(mapStateToProps, mapDispatchToProps)(ProfileQuestions)