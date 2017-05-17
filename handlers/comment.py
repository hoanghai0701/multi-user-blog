from handler import *
from utils.decorators import *


class CommentHandler(AjaxHandler):
    @post_exists
    def index(self, post_id):
        post = self.data['post']
        page = self.request.get('page', 0)
        page = int(page)
        limit = 5

        comments = post.comments \
            .ancestor(Comment.comment_key(Post.post_key())) \
            .order("-created_at").fetch(limit=limit, offset=limit * page)

        comments = [to_json(comment) for comment in comments]
        return self.json(comments, 200)

    @post_exists
    @authenticated
    def store(self, post_id):
        post = self.data['post']
        body = self.request.json
        content = body['content']

        if content:
            comment = Comment(user=self.user, post=post, content=content, parent=Comment.comment_key(Post.post_key()))
            comment.put()
            return self.json({'msg': 'Comment successfully', 'data': to_json(comment)}, 200)
        else:
            return self.json({'error': 'Missing content'}, 400)

    @comment_permission
    @comment_exists
    @post_exists
    @authenticated
    def update(self, post_id, comment_id):
        body = self.request.json
        content = body['content']

        if not content:
            return self.json({'error': 'Missing content'}, 400)

        comment = self.data['comment']
        comment.content = content
        comment.put()
        return self.json({'msg': 'Comment updated successfully', 'data': to_json(comment)}, 200)

    @comment_permission
    @comment_exists
    @post_exists
    @authenticated
    def destroy(self, post_id, comment_id):
        comment = self.data['comment']
        comment.delete()
        return self.json({'msg': 'Comment deleted successfully'}, 200)
