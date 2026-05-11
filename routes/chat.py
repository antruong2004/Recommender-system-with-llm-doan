from flask import Blueprint, jsonify, request


def create_chat_blueprint(services):
    advisor = services['advisor']
    db_service = services.get('db_service')

    bp = Blueprint('chat_api', __name__)

    @bp.route('/api/chat', methods=['POST'])
    def chat():
        data = request.json or {}
        user_message = data.get('message', '').strip()
        session_id = data.get('session_id', 'default')
        user_id = data.get('user_id') or None
        if not user_message:
            return jsonify({'error': 'Vui long nhap cau hoi'}), 400
        result = advisor.chat(user_message, session_id, user_id)

        if db_service:
            try:
                db_service.save_chat_message(session_id=session_id, user_id=user_id, role='user', content=user_message)
                db_service.save_chat_message(
                    session_id=session_id,
                    user_id=user_id,
                    role='assistant',
                    content=result.get('response', ''),
                )
            except Exception as exc:
                print(f"  [DB] Khong the luu chat: {exc}")

        return jsonify(result)

    @bp.route('/api/history/<session_id>', methods=['GET'])
    def get_history(session_id):
        if db_service:
            try:
                history = db_service.get_chat_history(session_id)
                return jsonify({'history': history, 'session_id': session_id, 'source': 'psql'})
            except Exception as exc:
                print(f"  [DB] Khong the doc lich su chat: {exc}")
        history = advisor.conversation_histories.get(session_id, [])
        return jsonify({'history': history, 'session_id': session_id, 'source': 'memory'})

    @bp.route('/api/history/<session_id>', methods=['DELETE'])
    def clear_history(session_id):
        if db_service:
            try:
                db_service.clear_chat_history(session_id)
            except Exception as exc:
                print(f"  [DB] Khong the xoa lich su chat: {exc}")
        advisor.conversation_histories.pop(session_id, None)
        return jsonify({'message': 'Da xoa lich su', 'session_id': session_id})

    return bp
