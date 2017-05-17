from handler import *


class LikeHandler(AjaxHandler):
    def store(self, post_id):
        post_id = int(post_id)
        post = Post.get_by_id(post_id, parent=Post.post_key())

        if not post:
            return self.json({'error': 'Post not found'}, 404)
        else:
            current_like = self.user.likes.ancestor(Like.like_key()).filter('post = ', post).get()
            if current_like:
                return self.json({'error': 'You already liked this post'}, 400)
            if post.user.key().id() == self.user.key().id():
                return self.json({'error': 'You cannot like your own post'}, 403)

            like = Like(user=self.user, post=post, parent=Like.like_key())
            like.put()
            post.num_likes += 1
            post.put()
            return self.json(
                {'msg': 'Like post successfully', 'data': {'like': to_json(like), 'num_likes': post.num_likes}}, 200)

    def destroy(self, post_id, like_id):
        post_id = int(post_id)
        post = Post.get_by_id(post_id, parent=Post.post_key())

        if not post:
            return self.json({'error': 'Post not found'}, 404)
        else:
            like_id = int(like_id)
            like = Like.get_by_id(like_id, parent=Like.like_key())
            if like.post.key().id() != post.key().id():
                return self.json({'error': 'This like does not belong to this post'}, 400)
            elif like.user.key().id() != self.user.key().id():
                return self.json({'error': 'You cannot delete this like'}, 403)
            else:
                like.delete()
                post.num_likes -= 1
                post.put()
                return self.json({'msg': 'Unlike successfully', 'data': {'num_likes': post.num_likes}}, 200)