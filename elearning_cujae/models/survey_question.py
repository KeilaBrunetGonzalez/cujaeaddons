from odoo import models, fields, api


class SurveyQuestion(models.Model):
    _inherit= 'survey.question'
    
    valid_answer_ids = fields.One2many(
        'survey.question.valid.answer',  # Nuevo modelo para respuestas válidas
        'question_id',
        string='Valid answers',
        
    )
    max_score = fields.Float(
        string='Max score',
        compute='_compute_question_max_score',
        store=True  # Opcional: Almacena el valor en la BD para mejor rendimiento
    )
    question_type = fields.Selection(
        selection_add=[('upload_file', 'Upload file')],
        help='Select the type of question to create.')
    upload_multiple_file = fields.Boolean(string='Upload multiple files',
                                          help='Check this box if you want to '
                                               'allow users to upload '
                                               'multiple files')

    @api.depends('answer_score', 'suggested_answer_ids', 'suggested_answer_ids.answer_score', 'suggested_answer_ids.is_correct')
    def _compute_question_max_score(self):
        """Calcula la puntuación máxima sumando el answer_score de la pregunta y sus suggested_answer_ids que tengan is_correct en True."""
        for question in self:
            # Suma del answer_score de la pregunta (0 si no está definido)
            question_score = question.answer_score or 0
            
            # Suma de los answer_score de todas las respuestas sugeridas CORRECTAS
            suggested_scores = sum(
                answer.answer_score for answer in question.suggested_answer_ids if answer.is_correct
            ) or 0
            
            question.max_score = question_score + suggested_scores

    




    @api.depends('question_type', 'scoring_type', 'answer_date', 'answer_datetime', 'answer_numerical_box')
    def _compute_is_scored_question(self):
        """ Computes whether a question "is scored" or not. Handles following cases:
          - inconsistent Boolean=None edge case that breaks tests => False
          - survey is not scored => False
          - 'date'/'datetime'/'numerical_box' question types w/correct answer => True
            (implied without user having to activate, except for numerical whose correct value is 0.0)
          - 'simple_choice / multiple_choice': set to True even if logic is a bit different (coming from answers)
          - question_type isn't scoreable (note: choice questions scoring logic handled separately) => False
        """
        for question in self:
            if question.question_type=='char_box' or question.question_type=='text_box' or question.question_type=='upload_file':
                question.is_scored_question = True
                question.scoring_type= 'scoring_with_answers'
                print("hello")
            elif question.question_type == 'date':
                question.is_scored_question = bool(question.answer_date)
            elif question.question_type == 'datetime':
                question.is_scored_question = bool(question.answer_datetime)
            elif question.question_type == 'numerical_box' and question.answer_numerical_box:
                question.is_scored_question = True
            elif question.question_type in ['simple_choice', 'multiple_choice']:  
                question.is_scored_question = True
            else:
                question.is_scored_question = False
            
    def action_add_question(self):
        """Summary:
              Function to view question wizard
           Returns:
               returns the  view of the 'question.wizard' view.
        """
        return {
            'name': "Add To Survey",
            'view_mode': 'form',
            'res_model': 'question.wizard',
            'type': 'ir.actions.act_window',
            'target': 'new',
        }  

    