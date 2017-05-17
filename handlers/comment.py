from handler import *


class CommentHandler(AjaxHandler):
    def index(self, post_id):
        post_id = int(post_id)
        post = Post.get_by_id(post_id, parent=Post.post_key())
        page = self.request.get('page', 0)
        page = int(page)
        limit = 5

        if not post:
            return self.json({'error': 'Post not found'}, 404)
        else:
            comments = post.comments \
                .ancestor(Comment.comment_key(Post.post_key())) \
                .order("-created_at").fetch(limit=limit, offset=limit * page)

            comments = [to_json(comment) for comment in comments]
            return self.json(comments, 200)

    def store(self, post_id):
        post_id = int(post_id)
        post = Post.get_by_id(post_id, parent=Post.post_key())
        body = self.request.json
        content = body['content']

        if not post:
            return self.json({'error': 'Post not found'}, 404)
        else:
            comment = Comment(user=self.user, post=post, content=content, parent=Comment.comment_key(Post.post_key()))
            comment.put()
            return self.json({'msg': 'Comment successfully', 'data': to_json(comment)}, 200)

    def update(self, post_id, comment_id):
        post_id = int(post_id)
        post = Post.get_by_id(post_id, parent=Post.post_key())
        body = self.request.json
        content = body['content']

        if not post:
            return self.json({'error': 'Post not found'}, 404)
        else:
            comment_id = int(comment_id)
            comment = Comment.get_by_id(comment_id, parent=Comment.comment_key(Post.post_key()))
            if comment.post.key().id() != post.key().id():
                return self.json({'error': 'This comment does not belong to this post'}, 400)
            elif comment.user.key().id() != self.user.key().id():
                return self.json({'error': 'You cannot edit this comment'}, 403)
            else:
                comment.content = content
                comment.put()
                return self.json({'msg': 'Comment updated successfully', 'data': to_json(comment)}, 200)

    def destroy(self, post_id, comment_id):
        post_id = int(post_id)
        post = Post.get_by_id(post_id, parent=Post.post_key())

        if not post:
            return self.json({'error': 'Post not found'}, 404)
        else:
            comment_id = int(comment_id)
            comment = Comment.get_by_id(comment_id, parent=Comment.comment_key(Post.post_key()))
            if comment.post.key().id() != post.key().id():
                return self.json({'error': 'This comment does not belong to this post'}, 400)
            elif comment.user.key().id() != self.user.key().id():
                return self.json({'error': 'You cannot delete this comment'}, 403)
            else:
                comment.delete()
                return self.json({'msg': 'Comment deleted successfully'}, 200)
